import pandas


# def timeparser(t):
#     return pandas.Timedelta(t, '%H:%M:%S')

TD0 = pandas.Timedelta(0)
TD1 = pandas.Timedelta("1D")


def readLogFile(filename):
    data = pandas.read_csv(
        filename,
        parse_dates=['Time'],
        # date_parser=timeparser,
        delim_whitespace=True,
    )
    data["Time"] = data["Time"] - data["Time"][0]

    while any(data["Time"] < TD0):
        data.loc[data["Time"] < TD0, "Time"] += TD1

    return data


if __name__ == '__main__':
    print(readLogFile(
        "../Data/Heating_1hr_480C.prc_2019-03-06_15-19-38_ProcessLog-Deposition System - TU Eindhoven.txt"
    ))
