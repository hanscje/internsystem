from datetime import datetime
from io import open
from os import walk
from os.path import isdir, isfile, join
from optparse import make_option
from pprint import pprint

import re
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone as tz

from cyb_oko.settings import TIME_ZONE
from z.models import Zrapport, Kvittering, Kassetransaksjon, KassenavnMapping

class Command(BaseCommand):
    args = '<file or directories ...>'
    help = 'Load the given z-report files into the database'

    #
    # Compiled regexes used to parse the input file
    #

    # Match all lines that we skip
    skip_lines = re.compile('^(\s$|\d[A-Z\/]|JOURNAL DES VENTES|FIN DE LECTURE|-D|B\s+\d+\s(TIROIR|TA|AT))')

    # Match the start date lines
    start_date = re.compile('^\/(\d{2}-\d{2}-\d{4} \d{2}:\d{2})')

    # Match the receipt transaction lines
    receipt_transaction = re.compile('^([a-zA-Z])\s+(\d+)\s(.{15})\s+(-?\d+)\s+(-?\d+\.\d{2})')

    # Match the receipt date line
    receipt_date = re.compile('^ <(\d{2}-\d{2}-\d{2} \d{2}:\d{2})(\d{6})')

    # Match the z-report date line
    z_number = re.compile('^\s+Z READING NR (\d+)')

    #
    # Timezone stuff
    #

    # Store the pytz timezone object for out current timezone
    tz = pytz.timezone(TIME_ZONE)

    def handle(self, *args, **options):
        print('Parsing in timezone: %s' % TIME_ZONE)

        for arg in args:
            self.parse_files(arg)

    def parse_files(self, path):
        if isdir(path):
            for root, dirs, files in walk(path):
                for file in files:
                    self.parse_file(join(root, file))
        elif isfile(path):
            self.parse_file(path)

    def parse_file(self, file):
        with open(file, 'rt', encoding='iso8859-1') as f:
            # Skip the first line
            f.readline()

            # Create models
            self.z = Zrapport()
            self.kvitteringer = []

            self.new_receipt()

            # Parse each line
            for line in f:
                self.parse_line(line)

            self.save_z()

    def new_receipt(self):
        # Store the previous receipt, if needed
        if hasattr(self, 'kvittering'):
            self.kvitteringer.append(self.kvittering)

        # Create a new one
        self.kvittering = Kvittering()
        self.kvittering.linjer = []

    def save_z(self):
        self.z.save()
        self.z.kvitteringer = self.kvitteringer
        #[l.save() for k in self.kvitteringer for l in k]

    def parse_line(self, line):
        if self.skip_lines.search(line):
            return
        elif self.receipt_date_line(line):
            self.new_receipt()
            return
        elif self.receipt_transaction_line(line):
            return
        elif self.z_number_line(line):
            return
        elif self.start_date_line(line):
            return
        else:
            raise Exception('Unknown line: %s' % line)

    def receipt_date_line(self, line):
        m = self.receipt_date.search(line)
        if m:
            self.kvittering.tidspunkt = self.tz.localize(datetime.strptime(m.group(1), '%d-%m-%y %H:%M'))
            self.kvittering.nummer = int(m.group(2), base=10)
            return True
        else:
            return False

    def receipt_transaction_line(self, line):
        m = self.receipt_transaction.search(line)
        if m:
            try:
                self.kvittering.linjer.append(
                        self.to_line(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)))
            except IgnoredLineException:
                pass
            return True
        else:
            return False

    def z_number_line(self, line):
        m = self.z_number.search(line)
        if m:
            self.z.nummer = int(m.group(1), base=10)
            return True
        else:
            return False

    def start_date_line(self, line):
        m = self.start_date.search(line)
        if m:
            if not self.z.tidspunkt:
                self.z.tidspunkt = self.tz.localize(datetime.strptime(m.group(1), '%d-%m-%Y %H:%M'))
            return True
        else:
            return False


    def to_line(self, code, number, name, count, sum):
        t = self.type(code)

        return {
                'type': self.type(code),
                'number': int(number),
                'name': name.strip(),
                'count': int(count),
                'sum': float(sum)
                }

    def type(self, code):
        if code == 'A':
            return 'sale'
        elif code == 'R':
            return 'payment'
        elif code == 'x':
            return 'tax'
        elif code == 'K':
            return 'refund'
        elif code == 'L':
            #return 'cancelled_sale'
            # Ignore canelled sales
            raise IgnoredLineException()
        elif code == 'c' or code == 'h':
            raise IgnoredLineException()
        else:
            raise UnknownLineException('Unknown line code: %s' % code)

class UnknownLineException(Exception):
    """
    Thrown when we find a linetype we do not support
    """
    pass

class IgnoredLineException(Exception):
    """
    An exception to throw when a line should be ignored
    """
    pass
