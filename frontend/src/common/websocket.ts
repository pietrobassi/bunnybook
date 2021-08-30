import { BehaviorSubject, Observable, Subject } from "rxjs";
import { filter, map } from "rxjs/operators";
import io from "socket.io-client";
import sioWildcard from "socketio-wildcard";
import { singleton } from "tsyringe";

export enum EventType {
  DEVICES_CHANGED = "events:devices-changed",
  RUNNING_SUITES_CHANGED = "events:running-suites-changed",
  PENDING_SUITES_CHANGED = "events:pending-suites-changed",
  SUITE_EXECUTION_COMPLETED = "events:suite-execution-completed",
  SUITE_RESULT_DELETED = "events:suite-result-deleted",
  SUITE_NOTES_CHANGED = "events:suite-notes-changed",
}

interface WsMessage {
  event: string;
  payload: any;
}

@singleton()
export class WebSocketService {
  public static pingIntervalMs: number = 5000;
  private _socket: SocketIOClient.Socket | null = null;
  private _connected$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(
    false
  );
  private _messages$: Subject<WsMessage> = new Subject();
  private _pingIntervalId: any;

  public readonly connected$: Observable<boolean> =
    this._connected$.asObservable();

  /**
   * Create websocket connection with backend and register event handlers.
   *
   * @param token jwt auth token
   */
  public connect(token?: string | null) {
    this._socket = io(process.env.REACT_APP_SOCKETIO_URL!, {
      path: "/ws/socket.io",
      transports: ["websocket", "xhr-polling"],
      upgrade: true,
      auth: { token },
    });

    sioWildcard(io.Manager)(this._socket as any);

    this._socket!.on("connect", () => {
      this._pingIntervalId = setInterval(
        () => this._socket?.emit("ping"),
        WebSocketService.pingIntervalMs
      );
      this._connected$.next(true);
    });

    this._socket!.on("disconnect", () => {
      clearInterval(this._pingIntervalId);
      this._connected$.next(false);
    });

    this._socket!.on("*", (msg: any) => {
      this._messages$.next({ event: msg.data[0], payload: msg.data[1] });
    });
  }

  /**
   * Disconnect and reconnect websocket instance.
   *
   * @param token jwt auth token
   */
  public reconnect(token: string) {
    this.disconnect();
    this.connect(token);
  }

  /**
   * Disconnect websocket instance.
   */
  public disconnect() {
    this._socket?.close();
  }

  /**
   * Listen to a specific message event type.
   *
   * @param eventType event name to listen to
   * @returns an Observable that emits message payload whenever and event of 'eventType' is received
   */
  public listenTo(eventType: string): Observable<any> {
    return this._messages$.asObservable().pipe(
      filter((msg) => msg.event === eventType),
      map((msg) => msg.payload)
    );
  }

  /**
   * Send a message to backend via websocket.
   *
   * @param event event name
   * @param message message payload
   * @param callback optional callback that is invoked if backend handler returns something
   */
  public send(
    event: string,
    message: any,
    callback: (...args: any[]) => any = (...args) => null
  ) {
    this._socket!.emit(event, message, callback);
  }
}
