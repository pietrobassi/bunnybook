import { BroadcastChannel } from "broadcast-channel";
import { Subject } from "rxjs";
import { singleton } from "tsyringe";
import { v4 as uuidv4 } from "uuid";

export interface ChannelMessage {
  event: string;
  payload?: any;
}

/**
 * Service used to communicate between different browser tabs (useful e.g. to synchronize login/logout between tabs).
 *
 * @export
 * @class BrowserTabsChannel
 */
@singleton()
export class BrowserTabsChannel {
  private _tabId = uuidv4();
  private _browserTabsChannel = new BroadcastChannel("bunny");
  private _messages$ = new Subject<ChannelMessage>();

  public readonly messages$ = this._messages$.asObservable();

  constructor() {
    this._browserTabsChannel.onmessage = (msg: any) => {
      if (msg._tabId !== this._tabId) {
        this._messages$.next(msg);
      }
    };
  }

  public postMessage(event: string, payload?: any): void {
    this._browserTabsChannel.postMessage({
      _tabId: this._tabId,
      event,
      payload,
    });
  }
}
