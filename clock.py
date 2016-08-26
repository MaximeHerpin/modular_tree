# Copyright 2016 Maxime Herpin, Jake Dube
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of Modular Tree.
#
# Modular Tree is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Modular Tree is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Modular Tree.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

from time import time


class Clock:
    """A quick and easy to use performance measuring tool.

    Methods:
        __init__ - Clocks the start time to measure performance.
        add_sub_job - Adds a sub-job to the job list.
        stop - Stops the specified job.
        display - Displays the final statistics.
    """
    def __init__(self, main_job):
        """Clocks the start time to measure performance.

        Args:
            job - (string) the name of the job to print out when finished

        """
        self.jobs = [[main_job, {"sublvl": 0,  "start": time(), "finish": 0}]]

    def add_sub_job(self, sub_job, sub=1):
        """Adds a sub-job to the job list.

        Args:
            sub_job - (string) the name of the sub_job to make
            sub - (int) the sub level (see details)

        Details:
            The sub property is used for if you want to time an entire function, but also
            a few lines in that function. The lines in the middle can be given a sub
            value of 1 to indicate that they are in the 2nd sub-level and they will be indented
            in the final printout.
        """
        self.jobs.append([sub_job, {"sublvl": sub, "start": time(), "finish": 0}])

    def stop(self, job):
        """Stops the specified job.

        Args:
            job - (string) the name of the job to stop
        """
        for i, j in enumerate(self.jobs):
            if j[0] == job:
                if self.jobs[i][1]["finish"]:
                    print("Job already finished!")
                else:
                    self.jobs[i][1]["finish"] = time()
                return self.jobs[i][1]["finish"] - self.jobs[i][1]["start"]

    def display(self):
        """Displays the final statistics."""
        for job in self.jobs:
            name = job[0]
            info = job[1]
            string = "{sub}{name} took {tm} seconds".format(
                name=name,
                sub="    " * info["sublvl"],
                tm=info["finish"] - info["start"])
            print(string)

