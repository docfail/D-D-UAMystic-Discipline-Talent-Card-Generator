import csv
import re
import fpdf

patt = r'Psychic Focus\.|[A-Z][a-zA-Z ]+\([0-9\W]*? psi.*?\)\.?|Bestial Transformation\.'
headerParse = re.compile(patt)
dataFile = open("./Psionics.csv", 'r')
dataReader = csv.reader(dataFile)
data = [x for x in dataReader]


class Discipline:
    def __init__(self, data_cluster):
        self.name = data_cluster[0]
        data_text = data_cluster[2]
        abilityNames = headerParse.findall(data_text)
        abilityText = [x.strip().encode('latin-1', 'ignore').decode('latin1') for x in headerParse.split(data_text)]
        self.description = abilityText[0]
        self.abilities = [x for x in zip(abilityNames, abilityText[1:])]
        self.is_talent = not (len(self.abilities) > 0)


dimensions = (2, 3)


class PDF(fpdf.FPDF):
    margin = 0.1
    margin_thickness = 0.02
    center_color = (200, 200, 200)
    outer_color = (200, 200, 200)
    line_color = (25, 25, 25)
    dist_to_inner = margin + margin_thickness
    title_height = 0.04
    desc_height = 0.12

    def print_lines(self):
        self.set_fill_color(*self.outer_color)
        self.rect(0, 0, dimensions[0], dimensions[1], 'DF')
        self.set_fill_color(*self.line_color)  # color for outer rectangle
        self.rect(self.margin, self.margin, dimensions[0] - (self.margin * 2), dimensions[1] - (self.margin * 2), 'DF')
        self.set_fill_color(*self.center_color)  # color for inner rectangle
        self.rect(self.dist_to_inner, self.dist_to_inner,
                  dimensions[0] - (self.dist_to_inner * 2), dimensions[1] - (self.dist_to_inner * 2),
                  'FD')

    def print_title(self, name):
        dist_to_inner = self.dist_to_inner
        inner_rect = (dimensions[0] - (dist_to_inner * 2), dimensions[1] - (dist_to_inner * 2))
        self.set_xy(dist_to_inner, dist_to_inner)
        self.set_font('Arial', 'B', 7)
        self.set_text_color(0, 0, 0)
        self.cell(w=inner_rect[0], h=inner_rect[1] * self.title_height, align='L', txt=name, border=1)

    def print_body(self, description, abilities, extra_small=False):
        dist_to_inner = self.dist_to_inner
        inner_rect = (dimensions[0] - (dist_to_inner * 2), (dimensions[1] - (dist_to_inner * 2)))
        desc_height = self.desc_height
        breathing_room = 0.03
        text_height = 0.06
        body_font_size = 4
        desc_font_size = 5
        if extra_small:
            desc_height = 0.8 * desc_height
            breathing_room = 0.025
            text_height = 0.05
            body_font_size = 4
            desc_font_size = 4
        # Print the dividing line
        y_level = dist_to_inner + (inner_rect[1] * (self.title_height + desc_height))
        self.line(dist_to_inner, y_level, dimensions[0] - dist_to_inner, y_level)
        # Set up and print description
        self.set_xy(dist_to_inner, dist_to_inner + (inner_rect[1] * self.title_height) + breathing_room)
        self.set_font('Arial', 'I', desc_font_size)
        self.set_margins(dist_to_inner, dist_to_inner)
        self.set_text_color(0, 0, 0)
        self.write(h=text_height, txt=description)
        # Print abilities
        self.set_xy(dist_to_inner, dist_to_inner + (inner_rect[1] * (self.title_height + desc_height)) + breathing_room)
        for pair in abilities:
            self.set_font('Arial', 'B', body_font_size)
            self.write(h=text_height, txt=(pair[0] + " "))
            self.set_font('Arial', '', body_font_size)
            self.write(h=text_height, txt=(pair[1] + "\n"))
        return self.get_y() > (dist_to_inner + inner_rect[1])

    def print_body_talent(self, description):
        dist_to_inner = self.dist_to_inner
        inner_rect = (dimensions[0] - (dist_to_inner * 2), (dimensions[1] - (dist_to_inner * 2)))
        breathing_room = 0.03
        text_height = 0.1
        desc_font_size = 6
        # Set up and print description
        self.set_xy(dist_to_inner, dist_to_inner + (inner_rect[1] * self.title_height) + breathing_room)
        self.set_font('Arial', 'I', desc_font_size)
        self.set_margins(dist_to_inner, dist_to_inner)
        self.set_text_color(0, 0, 0)
        self.write(h=text_height, txt=description)

    def print_page(self, disc: Discipline):
        self.add_page()
        self.print_lines()
        self.print_title(disc.name)
        if not disc.is_talent:
            if self.print_body(disc.description, disc.abilities):
                self.print_lines()
                self.print_title(disc.name)
                self.print_body(disc.description, disc.abilities, True)
        else:
            self.print_body_talent(disc.description)


disciplines = [Discipline(x) for x in data[1:]]

# test_discipline = disciplines[3]
# print("Name:{0}\nDescription:{1}\nAbilities:{2}".format(test_discipline.name, test_discipline.description, test_discipline.abilities))

pdf = PDF('P', 'in', dimensions)
pdf.set_auto_page_break(False)
for discipline in disciplines:
    pdf.print_page(discipline)
pdf.output('./discipline_cards.pdf', 'F')
