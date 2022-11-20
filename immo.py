import csv
class Immo:
    def __init__(self, source, id, link, rooms, surface, rent, kreis, floor, start_date):
        self.source = source
        self.id = id
        self.link = link
        self.rooms = rooms
        self.surface = surface
        self.rent = rent
        self.kreis = kreis
        self.floor = floor
        self.start_date = start_date

    def print(self):
        print("Source: " + self.source)
        print("ID: " + self.id)
        print("Link " + self.link)
        print("Rooms: " + self.rooms)
        print("surface: " + self.surface)
        print("rent: " + self.rent)
        print("kreis: " + self.kreis)
        print("floor: " + self.floor)
        print("start_date: " + self.start_date)

    def __repr__(self):
        return f"- 🏠 {self.source}, {self.link}, {self.rooms}, {self.surface}, {self.rent}, {self.kreis}, {self.floor} , {self.start_date}"

    def writeCSV(self, immoCSV):
        with open(immoCSV, 'a', encoding='UTF8') as f:
            # create the csv writer
            writer = csv.writer(f)

            # write a row to the csv file
            row = [self.source, self.id, self.link, self.rooms, self.surface, self.rent, self.kreis, self.floor,
                   self.start_date]
            writer.writerow(row)