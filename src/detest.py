"""
Run The Process
"""

import os
import logging
import click
import csv
import pandas as pd
from datetime import timedelta

from pandas import DataFrame


# import urllib3
# from di_scripts.talend_common import get_executable_id, determine_environment_name
# from di_scripts.talend_common_processing import run_execution

# urllib3.disable_warnings()


@click.command()
@click.option(
    "-f", "--file_location", type=str, required=False, help="Location of the file"
)
def main(file_location):
    """
    Script to run Process
    if you run this via a command line (you could pass this variable)
    """
    log_level = os.environ.get("LOGLEVEL", "INFO").upper()
    logging.basicConfig(level=log_level)

    # Root location of the file.  Hard coding for now but can be updated via command line
    if file_location is None:
        file_location = "/Users/lscuderi/Google Drive (lscuderi@kalebo.com.au)/Programming/Python/Data Engineering Test/Data/"

    # Read in Sites
    site_list, line_count = read_in_sites(file_location)

    # Consoldate into one data frame
    master_df = consolodate_date(site_list, file_location)

    # We could now write this data to an AWS data store
    # Assume code to write to datastore here

    logging.info("Data loaded into Datastore")

    # Create Analysis Variables
    # Could be different Python program which reads loaded data from a target source
    # In this program for convenience

    analysis = analyse(master_df)

    # Write output for Visualisation
    analysis.to_csv(file_location + "nmi_consolodated.csv", index=False)
    logging.info("Successful - Writing analysis file")

    return True


def analyse(master_df):
    """
    Add Variables for analysis of Days and Time
    """

    # Convert to day of week
    master_df["day_of_week"] = master_df["localtime"].dt.day_name()
    master_df["hour"] = master_df["localtime"].dt.hour

    # Drop variables not grouped
    master_df = master_df.drop(["AESTTime"], axis=1)
    master_df = master_df.drop(["localtime"], axis=1)

    # Use average per Day of week and hour
    analysis_df = (
        master_df.groupby(by=["nmi", "day_of_week", "hour"], group_keys=True)
        .mean()
        .reset_index()
    )

    # Find the 25% quantile for each site
    quantile_df = (
        analysis_df.drop(["hour"], axis=1)
        .drop(["day_of_week"], axis=1)
        .groupby(by=["nmi"], group_keys=True)
        .quantile(0.25)
        .reset_index()
    )

    # Rename column
    quantile_df = quantile_df.rename(columns={"Quantity_kWh": "Quantile"})

    # Join this data back on
    analysis_df = analysis_df.merge(quantile_df, on=("nmi"), how="left")

    return analysis_df


def consolodate_date(site_list, file_location):
    """
    Bring all sites into one file
    """
    # Append the data from the sites for analysis
    nmi_count = 0

    for element in site_list:
        nmi_df = read_in_nmi(
            file_location, element["nmi"], element["state"], element["interval"]
        )
        nmi_count += 1

        # Filter out missing DateTimes
        # print(nmi_df[ nmi_df['AESTTime'].isnull() == False ] )
        nmi_df = nmi_df.dropna()

        # df['AESTTime'] isna()

        if nmi_count == 1:
            master_df = nmi_df
        else:
            master_df = pd.concat([master_df, nmi_df])

    return master_df


def normalise_unit(quantity, unit):
    """
    Normalises unit to same unit of kWH
    expected input Wh, kWH, MWh
    """
    if unit.lower() == "wh":
        return quantity / 1000
    elif unit.lower() == "kwh":
        return quantity
    elif unit.lower() == "mwh":
        return quantity * 1000
    else:
        raise ValueError(f"Unsupported unit: {unit}")


def normalise_time(time, state):
    """
    Normalises time to local time with input of a State
    assumption that AEST does not change for daylight saving
    """
    if state.upper() in ["QLD", "VIC", "NSW", "TAS", "ACT"]:
        return time
    elif state.upper() in ["NT", "SA"]:
        return time - timedelta(minutes=30)
    elif state.upper() in ["WA"]:
        return time - timedelta(hours=2)
    else:
        logging.info("D")
        raise ValueError(f"Unsupported State: {state}")


def read_in_nmi(file_location, nmi, state, interval):
    """
    Read in control NMI Data which is the list of NMI that we are interested in
    Data Structure
    MNI, State, Interval
    """
    logging.info(f"Attempting loading {nmi}.csv for State  {state}")
    try:
        datafile = file_location + "ConsumptionData/" + nmi + ".csv"
        df = pd.read_csv(datafile)

        df["nmi"] = nmi

        # Normalise Unit
        df["Quantity_kWh"] = df.apply(
            lambda row: normalise_unit(row["Quantity"], row["Unit"]), axis=1
        )

        # Convert to Local Time
        # Normalise Time
        df["localtime"] = pd.to_datetime(df["AESTTime"], format="mixed")
        df["localtime"] = df.apply(
            lambda row: normalise_time(row["localtime"], state), axis=1
        )

        # Remove Cleaned up Fields
        # This is optional if we want to keep the origainl data
        df = df.drop(["Quantity"], axis=1)
        df = df.drop(["Unit"], axis=1)

    except:
        logging.warning(f"Data file not found for {nmi}.csv - skipping processing")
        return pd.DataFrame({})

    return df


def read_in_sites(file_location):
    """
    Read in control NMI Data which is the list of NMI that we are interested in
    Data Structure
    MNI, State, Interval
    """

    controlfile = file_location + "nmi_info.csv"
    # Open control file
    # The code could be improved to use the headers to dynamically create the variable names.
    # Kept this way for simplicity for now
    with open(controlfile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        site_data = []
        for row in csv_reader:
            if line_count == 0:
                logging.debug(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                if len(row) != 0:
                    site = {"nmi": row[0], "state": row[1], "interval": row[2]}
                    line_count += 1
                    logging.debug(site)
                    site_data.append(site)
                else:
                    logging.info("Blank line found - skipping")

        logging.info(f"Processed {line_count} lines.")

    return site_data, line_count


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
