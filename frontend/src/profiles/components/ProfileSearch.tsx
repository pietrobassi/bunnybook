import { useEffect, useRef, useState } from "react";
import {
  distinctUntilChanged,
  of,
  Subject,
  switchMap,
  takeUntil,
  throttleTime,
} from "rxjs";

import ProfileImage from "../../common/components/ProfileImage";
import { routerHistory } from "../../common/router";
import { profilesApi } from "../api";
import { Profile } from "../model";

const QUERY_THROTTLE_TIME = 750;

const ProfileSearch = () => {
  const [query, setQuery] = useState<string>("");
  const [matchingProfiles, setMatchingProfiles] = useState<Profile[]>([]);

  const debouncer$ = useRef(new Subject<string>()).current;
  const stopper$ = useRef(new Subject<void>()).current;

  const searchProfiles = (newQuery: string) => {
    if (newQuery.length) {
      profilesApi.searchProfiles(newQuery).then((profiles) => {
        setMatchingProfiles(profiles);
      });
    } else {
      setMatchingProfiles([]);
    }
  };

  useEffect(() => {
    const sub = debouncer$
      .pipe(
        switchMap((inputText: string) =>
          of(inputText).pipe(
            distinctUntilChanged(),
            throttleTime(QUERY_THROTTLE_TIME, undefined, { trailing: true }),
            takeUntil(stopper$)
          )
        )
      )
      .subscribe((newQuery) => searchProfiles(newQuery));
    return () => sub.unsubscribe();
  }, [debouncer$, stopper$]);

  const queryChangeHandler = (newQuery: string) => {
    setQuery(newQuery);
    debouncer$.next(newQuery);
  };

  const focusHandler = () => {
    searchProfiles(query);
  };

  const blurHandler = () => {
    stopper$.next();
    setMatchingProfiles([]);
  };

  const selectProfileHandler = (profileId: string) => {
    setQuery("");
    routerHistory.push(`/profile/${profileId}`);
    setMatchingProfiles([]);
  };

  return (
    <>
      <div className="dropdown is-active">
        <div className="dropdown-trigger">
          <div className="field">
            <p className="control is-expanded has-icons-right">
              <input
                className="input"
                type="search"
                value={query}
                onChange={(e) => queryChangeHandler(e.target.value)}
                onFocus={focusHandler}
                onBlur={blurHandler}
                placeholder="Search bunnies..."
              />
              <span className="icon is-small is-right">
                <i className="fas fa-search"></i>
              </span>
            </p>
          </div>
        </div>
        <div className="dropdown-menu" id="dropdown-menu" role="menu">
          <div className="dropdown-content pt-0 pb-0">
            {matchingProfiles.map((profile) => (
              // eslint-disable-next-line
              <a
                onMouseDown={() => selectProfileHandler(profile.id)}
                key={profile.id}
                className="dropdown-item p-0 is-flex is-align-items-center"
              >
                <figure className="image is-32x32 is-inline-block m-1 ml-2 is-flex-shrink-0">
                  <ProfileImage username={profile.username} />
                </figure>
                <span className="ml-1">{profile.username}</span>
              </a>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

export default ProfileSearch;
