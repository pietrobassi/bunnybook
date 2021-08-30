import { BehaviorSubject } from "rxjs";

/**
 * Utility function to ease loading of paginated results; call the returned function object to load next data page.
 *
 * @param data$ BehaviorSubject containing data result
 * @param isFetchingData$ BehaviorSubject that determines whether new results are being fetched
 * @param noMoreData$ BehaviorSubject that determines whether there are more results to be fetched or not
 * @param queryLimit limit parameter of paginated API
 * @param apiCall function to be called to fetch more results
 * @param reverse invert results order
 * @param runAfterNewDataFetched callback invoked right after new data has been fetched
 * @param keysetPaginationField field used for keyset pagination
 * @returns function to call when new results must be fetched
 */
export const loadPaginatedResults = (
  data$: BehaviorSubject<any[]>,
  isFetchingData$: BehaviorSubject<boolean>,
  noMoreData$: BehaviorSubject<boolean>,
  queryLimit: number,
  apiCall: (olderThan?: string) => Promise<any[]>,
  reverse: boolean = false,
  runAfterNewDataFetched: (data: any[]) => void = () => null,
  keysetPaginationField: string = "createdAt"
): (() => void) => {
  return () => {
    if (isFetchingData$.value || noMoreData$.value) {
      return;
    }
    isFetchingData$.next(true);
    const olderThan = data$.value.length
      ? data$.value[reverse ? 0 : data$.value.length - 1][keysetPaginationField]
      : undefined;
    apiCall(olderThan)
      .then((data) => {
        runAfterNewDataFetched(data);
        data$.next(
          reverse
            ? [...data.reverse(), ...data$.value]
            : [...data$.value, ...data]
        );
        if (data.length < queryLimit) {
          noMoreData$.next(true);
        }
      })
      .finally(() => isFetchingData$.next(false));
  };
};
