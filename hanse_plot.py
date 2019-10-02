# -*- coding: utf-8 -*-
from __future__ import division
import rc
import hanse_parse
import pylab
import datetime

EURO_PER_MONTH = 35

if __name__ == '__main__':
    print("getting data from internet...")
    hanse = hanse_parse.HanseBrowser()
    checkins = hanse.get_checkins()
    hanse_parse.save_checkins("checkins.dat", checkins)

    print("plotting...")
    dates = [checkin.date_start for checkin in checkins]
    ends = [checkin.date_end for checkin in checkins]
    durations = [checkin.duration for checkin in checkins]
    locations = [checkin.location for checkin in checkins]

    unique_locations = set(locations)

    colormap = dict()
    for loc, color in zip(unique_locations, rc.color_cycle):
        colormap.update({loc: color})
    print(colormap)

    fig, ax = pylab.subplots()

    for datetime_start, datetime_end, duration, location in zip(dates, ends, durations, locations):
        color = colormap[location]
        date_no_hour = datetime_start.date()
        hour_start = datetime_start.hour + datetime_start.minute/60
        hour_end = datetime_end.hour + datetime_end.minute/60
        size = duration.seconds/60

        pylab.bar(datetime.datetime(date_no_hour.year, date_no_hour.month, date_no_hour.day, hour=12),
                  duration.seconds/3600,
                  bottom=hour_start,
                  width=0.7,
                  color=color,
                  linewidth=0,
                  align="center")

    for loc in unique_locations:
        color = colormap[loc]
        pylab.plot(dates[0], 0, label=loc, linewidth=10)

    # axes limits and labels
    ax.set_ylim([8, 24])
    ax.set_yticks(range(8, 25, 4))
    ax.set_ylabel("Uhrzeit")
    ax.set_xlabel("Datum")

    padding = datetime.timedelta(days=1)
    day_from = min(dates) - padding
    day_to = datetime.datetime.today()
    num_days_plot = (day_to - day_from).days
    ax.set_xlim([day_from, day_to])
    fig.autofmt_xdate()

    # Kernzeit!
    ax.fill_between([day_from, day_to], 9, 12, facecolor="lightgray", linewidth=0)
    ax.fill_between([day_from, day_to], 14, 16, facecolor="lightgray", linewidth=0)

    # weekends!
    for day in [day_from.date() + datetime.timedelta(days=d) for d in range(num_days_plot+1)]:
        if day.weekday() >= 5: # 5,6 = sat/sun
            ax.fill_between([day, day + datetime.timedelta(days=1)], 0, 24,
                            facecolor="lightgray", linewidth=0)

    pylab.legend(numpoints=1, loc="lower left")

    title = "{} Checkins in {} Tagen".format(len(checkins), num_days_plot)
    title += u"\n {:.2f} € pro Checkin".format(EURO_PER_MONTH * 12 / 365 * num_days_plot / len(checkins))
    pylab.suptitle(title)

    pylab.show()
