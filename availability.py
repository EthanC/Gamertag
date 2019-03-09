import json
import re
import sys
import time

import requests
from colorama import Fore, init


def main():
    startTime = time.time()

    # Initialize Colorama.
    init(autoreset=True)

    print(Fore.CYAN + "Gamertag - Bulk Xbox Live Gamertag availability checker")
    print(Fore.CYAN + "https://github.com/EthanC/Gamertag\n")

    authorization, reservationID = LoadCredentials()
    gamertags = LoadList()

    print(f"Checking availability of {'{:,}'.format(len(gamertags))} gamertags...")

    gamertags = VerifyGamertags(gamertags)
    count = CheckAvailability(authorization, reservationID, gamertags)

    if count >= 1:
        print(Fore.GREEN + f"Saved {'{:,}'.format(count)} available gamertag(s)")

    endTime = int(time.time() - startTime)
    print(f"\nCompleted in {'{:,}'.format(endTime)}s")


def LoadCredentials():
    """Return credential values from credentials.json."""

    try:
        with open("credentials.json", "r") as credentialsFile:
            credentials = json.load(credentialsFile)

        authorization = credentials["authorization"]
        reservationID = credentials["reservationID"]

        return authorization, reservationID
    except Exception as e:
        print(Fore.RED + f"Failed to load credentials. {e}.")


def LoadList():
    """Return gamertags from list.txt."""

    try:
        with open("list.txt", "r") as listFile:
            gamertagList = listFile.readlines()

        gamertags = [gamertag.strip() for gamertag in gamertagList]

        return gamertags
    except Exception as e:
        print(Fore.RED + f"Failed to load gamertag list. {e}.")


def VerifyGamertags(gamertags):
    """Return a list of gamertags which meet the Xbox Live gamertag specifications."""

    i = 0
    for gamertag in gamertags:
        if len(gamertag) > 15:
            print(
                Fore.LIGHTBLACK_EX
                + f"Skipping gamertag {gamertag}, length {len(gamertag)} when maximum 15"
            )
            del gamertags[i]

        valid = bool(re.match("^[a-zA-Z0-9 ]+$", gamertag))
        if valid is False:
            print(
                Fore.LIGHTBLACK_EX
                + f"Skipping gamertag {gamertag}, contains invalid characters"
            )
            del gamertags[i]

        i = i + 1

    return gamertags


def CheckAvailability(authorization, reservationID, gamertags):
    """Return a list of gamertags which are available for purchase on Xbox Live."""

    count = 0

    for gamertag in gamertags:
        headers = {"Authorization": authorization, "Content-Type": "application/json"}
        payload = {"gamertag": gamertag, "reservationId": reservationID}

        req = requests.post(
            "https://user.mgt.xboxlive.com/gamertags/reserve",
            headers=headers,
            json=payload,
        )

        # HTTP 409 (Conflict).
        if req.status_code == 409:
            print(Fore.LIGHTBLACK_EX + f"Gamertag {gamertag} is unavailable")

        # HTTP 200 (OK).
        if req.status_code == 200:
            print(Fore.GREEN + f"Gamertag {gamertag} is available")
            SaveAvailable(gamertag)
            count += 1

        # HTTP 400 (Bad Request).
        if req.status_code == 400:
            print(
                Fore.RED
                + f"Failed to check gamertag {gamertag} availability. HTTP {req.status_code}."
            )
            print(req.text)

        # HTTP 401 (Unauthorized).
        if req.status_code == 401:
            print(
                Fore.RED
                + f"Failed to check gamertag {gamertag} availability, not authorized. HTTP {req.status_code}."
            )
            print(req.text)

        # HTTP 429 (Too Many Requests).
        # Allowed 10 requests in 15 seconds OR 50 requests in 300 seconds.
        if req.status_code == 429:
            res = json.loads(req.text)
            currentReq = res["currentRequests"]
            maxReq = res["maxRequests"]
            period = res["periodInSeconds"]

            print(
                Fore.RED
                + f"Rate Limited ({currentReq}/{maxReq} {period}s), sleeping for 15 seconds..."
            )
            time.sleep(15)

        req.close()

        # Ensure we're avoiding the 10 requests in 15 seconds rate limit.
        time.sleep(1.5)

    return count


def SaveAvailable(gamertag):
    """Write an available gamertag to the end of available.txt."""

    try:
        with open("available.txt", "a") as availableFile:
            availableFile.write(f"{gamertag}\n")
    except Exception as e:
        print(Fore.RED + f"Failed to save list of available gamertags. {e}.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
