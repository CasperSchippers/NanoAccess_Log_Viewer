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
        encoding="unicode escape"
    )
    data["Time"] = data["Time"] - data["Time"][0]

    while any(data["Time"] < TD0):
        data.loc[data["Time"] < TD0, "Time"] += TD1

    return data

