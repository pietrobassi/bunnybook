import { useCallback, useEffect, useRef, useState } from "react";
import { Observable } from "rxjs";
import { container, InjectionToken } from "tsyringe";

import { User } from "../auth/model";
import { AuthService } from "./../auth/service";

/**
 * Return an object that changes whenever the underlying observable emits a new value.
 *
 * @param observable observable to listen to
 * @param defaultValue returned object default value (needed if observable is not a BehaviorSubject hence doesn't have
 * an initial value)
 * @returns object
 */
export const useObservable = <T>(
  observable: Observable<T>,
  defaultValue?: T
): T => {
  const [state, setState] = useState<T>(
    defaultValue !== undefined
      ? defaultValue
      : (observable as any).source.getValue()
  );
  useEffect(() => {
    const sub = observable.subscribe(setState);
    return () => sub.unsubscribe();
  }, [observable]);

  return state;
};

/**
 * Inject a service into a component through dependency injection.
 *
 * @param token injection token (e.g. class name of injectable resource)
 * @returns service instance
 */
export const useService = <T>(token: InjectionToken<T>): T => {
  const service = useRef() as any;
  if (!service.current) {
    service.current = container.resolve(token as InjectionToken<T>);
  }
  return service.current;
};

/**
 * Return current logged (or anonymous) user; value changes whenever logged user changes.
 *
 * @returns User instance
 */
export const useUser = (): User => {
  return useObservable(useService(AuthService).user$);
};

/**
 * Register a callback that gets executed whenever the vertical scrollbar approaches the bottom of the page.
 *
 * @param callback callback function to invoke
 * @param windowPercentageTrigger vertical scrollbar callback trigger point, expressed as percentage of window height
 * @returns scroll handler callback
 */
export const useOnScrollToBottom = (
  callback: () => any,
  windowPercentageTrigger: number = 0.75
): (() => void) => {
  const scrollHandler = useCallback(() => {
    const bottomReached =
      Math.ceil(window.innerHeight + window.scrollY) >=
      document.documentElement.scrollHeight -
        window.innerHeight * windowPercentageTrigger;

    if (bottomReached) {
      callback();
    }
  }, [callback, windowPercentageTrigger]);

  useEffect(() => {
    window.addEventListener("scroll", scrollHandler, {
      passive: true,
    });
    return () => {
      window.removeEventListener("scroll", scrollHandler);
    };
  }, [scrollHandler]);

  return scrollHandler;
};
