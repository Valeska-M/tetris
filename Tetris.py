#region Setup
import pygame,os,math,random

    #region Pfade setzen
absolutepath = os.path.abspath(__file__)
fileDirectory = os.path.dirname(absolutepath)
os.chdir(fileDirectory)

Pfad_Schrift = str(fileDirectory) + "/Righteous-Regular.ttf"
    #endregion Pfade setzen

    #region Farben 
WEISS = (255,255,255)
SCHWARZ = (0,0,0)
GRUEN = (168,189,132)
ROT = (255,157,141)
TUERKIS = (171,221,255)
BLAU = (162,186,227)
LILA = (191,119,166)
ROSA = (255,163,173)
WEIN = (196,109,131)
CREME = (255,240,223)
GELB = (245,187,132)
BRAUN1 = (209,160,127)
HELLGRAU = (240,240,240)
MITTELGRAU = (220,220,220)
DUNKELGRUEN = (124,135,65)
    #endregion Farben

    #region Variablen
Level = "Menue"
Width = 900
Height = 600
Höhe_in_Blöcken = 21
Blockhöhe = math.ceil(Height/Höhe_in_Blöcken)
Breite_in_Blöcken = int(math.ceil(Width/Blockhöhe)) #in Blöcken angegeben
Breite_Spielfeld = 10 #Tatsächlich bespielbares Feld, muss gerade Zahl sein
Abgerundete_Ecken = int(Blockhöhe/4)
Neu_im_Level = True
Resize = False
Liste_Formen = ["I","Q","J","L","Z","S","T"]
K_down = False
Schriftfarbe1 = DUNKELGRUEN
Schriftfarbe2 = ROT
Schriftobjekte = {}
    #endregion Variablen

    #region Klassen und Funktionen
def Schrift_laden(Größe):
    if Größe not in Schriftobjekte:
        Schriftobjekte[Größe] = pygame.font.Font(Pfad_Schrift, Größe)
    return Schriftobjekte[Größe]

def Koordinaten_zu_Pixelposition(Position_x,Position_y): #Für Koordinaten, die in Spielfeld-Blöcken angegeben sind
    x_neu = Width/2-(Breite_Spielfeld/2)*Blockhöhe+Position_x*Blockhöhe
    y_neu = Position_y*Blockhöhe
    return(x_neu,y_neu)

def Stein_malen(Position_x,Position_y,Farbe,Blockhöhe,Radius_Ecken,Schatten=False):
    Pixel_x,Pixel_y = Koordinaten_zu_Pixelposition(Position_x,Position_y)
    Farbe_Highlight=(Farbe[0]+(255-Farbe[0])//4,Farbe[1]+(255-Farbe[1])//4,Farbe[2]+(255-Farbe[2])//4)
    if not Schatten:
        R = pygame.Rect(Pixel_x,Pixel_y,Blockhöhe,Blockhöhe)
        pygame.draw.rect(screen,Farbe,R,border_radius=Radius_Ecken)
        R = pygame.Rect(Pixel_x+Blockhöhe//8*3, Pixel_y+Blockhöhe//8, Blockhöhe//2,Blockhöhe//8)
        pygame.draw.rect(screen,Farbe_Highlight,R,border_radius=Blockhöhe//16)
    else:
        R = pygame.Rect(Pixel_x,Pixel_y,Blockhöhe,Blockhöhe)
        pygame.draw.rect(screen,Farbe_Highlight,R,border_radius=Radius_Ecken,width=Blockhöhe//8)

def Liste_Spielfeld_malen(Liste_Spielfeld,Blockhöhe,Radius_Ecken):
    for i in range(len(Liste_Spielfeld)):
        for j in range(len(Liste_Spielfeld[i])):
            if Liste_Spielfeld[i][j] == None:
                continue
            Farbe = Liste_Spielfeld[i][j]
            Stein_malen(j,i,Farbe,Blockhöhe,Radius_Ecken)

def Fallmöglichkeit(Figur,Liste_Spielfeld):
    Fallen_möglich_gesamt = Höhe_in_Blöcken #gibt an, um wie viele Zeilen die Figur maximal noch nach unten fallen kann
    for Punkt in Figur.liste:
        Position_x = math.floor(Figur.x) + Punkt[0]
        Position_y = math.floor(Figur.y) + Punkt[1]
        if Position_y == len(Liste_Spielfeld)-1:
            return(0)
        Fallen_möglich = 0
        for i in range(Position_y+1,len(Liste_Spielfeld)): #Zählen, wie viele freie Felder unter dem Punkt zur Verfügung stehen
            if i < 0:
                continue #Punkte überspringen, die oberhalb des Spielfeldes liegen
            if Liste_Spielfeld[i][Position_x] != None:
                # Fehlermeldung:
                # if Liste_Spielfeld[i][Position_x] != None:
                # IndexError: list index out of range
                break
            Fallen_möglich += 1
        Fallen_möglich_gesamt = min(Fallen_möglich_gesamt,Fallen_möglich)
    return(Fallen_möglich_gesamt)

def verschieben_möglich(Figur,Liste_Spielfeld,Verschiebung):
    for Punkt in Figur.liste: #testet für jeden Punkt, ob Verschiebung gültig
        x_neu = int(Figur.x + Punkt[0] + Verschiebung)
        y_neu = int(math.floor(Figur.y) + Punkt[1])
        if y_neu < 0:
            continue #Punkte überspringen, die über dem Spielfeld liegen
        if x_neu < 0 or x_neu >= len(Liste_Spielfeld[0]):
            return(False) #Wenn Außerhalb des Spielfeldes
        if Liste_Spielfeld[y_neu][x_neu] != None:
            return(False) #Wenn Feld bereits belegt
    return(True)

def Lösen(Liste_Spielfeld):
    # gelöste Zeilen ermitteln
    L_Zeilen = []
    for i in range(len(Liste_Spielfeld)): #Zeilen durchgehen
        Zeile_gelöst = True
        for j in range(len(Liste_Spielfeld[i])):
            if Liste_Spielfeld[i][j] == None:
                Zeile_gelöst = False
        if Zeile_gelöst:
            L_Zeilen.append(i)
    return(L_Zeilen)

def Menü_erstellen(Position_x, Position_y, Breite, Höhe, Farbe, Schriftfarbe, Liste_Button_Texte):
    #Teiler, um die Höhe der Buttons in Abhängigkeit von ihrer Anzahl zu ermitteln
    Teiler = 2*len(Liste_Button_Texte) + len(Liste_Button_Texte) - 1 
    Halbe_Höhe_Button = Höhe/Teiler
    L_Buttons = []
    for i in range(len(Liste_Button_Texte)):
        Knopf = Button(Position_x, Position_y + i*3*Halbe_Höhe_Button,Breite,2*Halbe_Höhe_Button,Farbe,Schriftfarbe,Liste_Button_Texte[i])
        L_Buttons.append(Knopf)
    return(L_Buttons)

class Button:
    def __init__(self,Position_x,Position_y,Breite,Höhe,Farbe,Schriftfarbe,Text):
        self.x = Position_x
        self.y = Position_y
        self.width = Breite
        self.height = Höhe
        self.color = Farbe
        self.font_color = Schriftfarbe
        self.text = Text
        self.ecken = int(self.height*Blockhöhe/2)
        Pixel_x,Pixel_y = Koordinaten_zu_Pixelposition(self.x,self.y)
        self.rect = pygame.Rect(Pixel_x,Pixel_y,self.width*Blockhöhe,self.height*Blockhöhe)
    def malen(self):
        #Stein
        R = self.rect
        pygame.draw.rect(screen,self.color,R,border_radius=self.ecken)
        #Highlight
        Pixel_x,Pixel_y = Koordinaten_zu_Pixelposition(self.x+self.width/4,self.y+self.height/8)
        Farbe_Highlight=(self.color[0]+(255-self.color[0])//4,self.color[1]+(255-self.color[1])//4,self.color[2]+(255-self.color[2])//4)
        R = pygame.Rect(Pixel_x, Pixel_y, Blockhöhe*self.width//8*5,self.height*Blockhöhe//8)
        pygame.draw.rect(screen,Farbe_Highlight,R,border_radius=int(self.height*Blockhöhe//16))
        #Schrift
        font = Schrift_laden(int(Blockhöhe*8/10))
        surface = font.render(self.text,True,self.font_color)
        Text_x,Text_y = Koordinaten_zu_Pixelposition(Breite_Spielfeld/2,self.y+self.height/2)
        screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))

class Figur:
    def __init__(self,Position_x,Position_y,Form): #Die Position wird relativ zur oberen linken Ecke des Spielfelds angegeben
        self.x = Position_x
        self.y = Position_y
        self.drehbar = True
        self.form = Form
        if Form == "I":
            self.farbe = TUERKIS
            self.liste = [(0,0),(-1,0),(1,0),(2,0)]
            self.breite = 4
        elif Form == "Q":
            self.drehbar = False
            self.farbe = GELB
            self.liste = [(0,0),(-1,0),(0,-1),(-1,-1)]
            self.breite = 2
        elif Form == "J":
            self.farbe = BLAU
            self.liste = [(0,0),(-1,0),(-1,-1),(1,0)]
            self.breite = 3
        elif Form == "L":
            self.farbe = BRAUN1
            self.liste = [(0,0),(-1,0),(1,-1),(1,0)]
            self.breite = 3
        elif Form == "Z":
            self.farbe = ROT
            self.liste = [(0,0),(0,-1),(1,0),(-1,-1)]
            self.breite = 3
        elif Form == "S":
            self.farbe = GRUEN
            self.liste = [(0,0),(0,-1),(1,-1),(-1,0)]
            self.breite = 3
        elif Form == "T":
            self.farbe = LILA
            self.liste = [(0,0),(-1,0),(0,-1),(1,0)]
            self.breite = 3
    def malen(self):
        for Punkt in self.liste:
            Position_x = self.x + Punkt[0]
            Position_y = math.floor(self.y) + Punkt[1]
            Stein_malen(Position_x,Position_y,self.farbe,Blockhöhe,Abgerundete_Ecken)
    def schatten(self,maximale_Fallhöhe):
        for Punkt in self.liste:
            Position_x = math.floor(self.x) + Punkt[0]
            Position_y = math.floor(self.y) + Punkt[1] + maximale_Fallhöhe
            Stein_malen(Position_x,Position_y,self.farbe,Blockhöhe,Abgerundete_Ecken,Schatten=True)
    def in_Liste(self,Liste_Spielfeld):
        for Punkt in self.liste:
            Position_x = math.floor(self.x) + Punkt[0]
            Position_y = math.floor(self.y) + Punkt[1]
            Liste_Spielfeld[Position_y][Position_x] = self.farbe
        return(Liste_Spielfeld)
    def drehen(self,Liste_Spielfeld):
        if not self.drehbar: # für nicht drehbare Formen
            return(self.liste)
        Punkteliste_neu = []
        Problem_links = False
        Problem_rechts = False
        for Punkt in self.liste:
            x_neu = -1*Punkt[1] 
            y_neu = Punkt[0]
            Position_x = int(self.x + x_neu)
            Position_y = int(math.floor(self.y) + y_neu)
            # überprüfen, ob Drehung möglich
            if Position_y >= len(Liste_Spielfeld): # Form würde unten überstehen
                return(self.liste)
            if Position_y < 0:
                Punkteliste_neu.append((x_neu,y_neu))
                continue #Punkte überspringen, die über dem Spielfeld liegen
            if Position_x < 0:
                Problem_links = True # steht links über
            elif Position_x >= len(Liste_Spielfeld[0]):
                Problem_rechts = True # steht rechts über
            elif Liste_Spielfeld[Position_y][Position_x] != None:
                if x_neu > 0: 
                    Problem_rechts = True
                elif x_neu < 0:
                    Problem_links = True
                else:#Form nicht drehbar, weil sie oben oder unten überlappen würde
                    return(self.liste) 
            Punkteliste_neu.append((x_neu,y_neu))
        if Problem_links == False and Problem_rechts == False: # no Problemo
            return(Punkteliste_neu)
        if Problem_links and Problem_rechts: # da ist nix mehr zu retten
            return(self.liste)
        # Bei einseitigem Problem: testen, ob Verschieben um 1 hilft
        Figur_gedreht = Figur(self.x,self.y,self.form)
        Figur_gedreht.liste = Punkteliste_neu
        Punkteliste_neu = []
        if Problem_links:
            if verschieben_möglich(Figur_gedreht,Liste_Spielfeld,1):
                for Punkt in Figur_gedreht.liste:
                    Punkt_verschoben = (Punkt[0]+1,Punkt[1])
                    Punkteliste_neu.append(Punkt_verschoben)
                return(Punkteliste_neu)
            else:
                return(self.liste)
        if Problem_rechts:
            if verschieben_möglich(Figur_gedreht,Liste_Spielfeld,-1):
                for Punkt in Figur_gedreht.liste:
                    Punkt_verschoben = (Punkt[0]-1,Punkt[1])
                    Punkteliste_neu.append(Punkt_verschoben)
                return(Punkteliste_neu)
            else:
                return(self.liste)

    #endregion Klassen und Funktionen

#endregion Setup

#region Spiel

    #region Spielstart & Ereignisse
pygame.init()
screen = pygame.display.set_mode((Width,Height),pygame.RESIZABLE)
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

running = True
while running:
    # Maus und Tasten zurücksetzen
    mx = my = -1
    K_rechts = False
    K_links = False
    K_up = False
    # Events abfragen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            (mx,my) = pygame.mouse.get_pos()
        if event.type == pygame.VIDEORESIZE:
            (Width,Height) = screen.get_size()
            Blockhöhe = math.ceil(Height/Höhe_in_Blöcken)
            Breite_in_Blöcken = math.ceil(Width/Blockhöhe) 
            Abgerundete_Ecken = int(Blockhöhe/4)
            Resize = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                K_rechts = True  
            if event.key == pygame.K_LEFT:
                K_links = True  
            if event.key == pygame.K_UP:
                K_up = True  
            if event.key == pygame.K_DOWN:
                K_down = True  
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                K_down = False  
    screen.fill(HELLGRAU)    
    #endregion Spielstart & Ereignisse

    #region Rand aufbauen
    Breite_Rand = (Breite_in_Blöcken-Breite_Spielfeld)//2+1
    for i in range(Breite_Rand): #Index, um Position der Randblöcke aufzubauen
        for j in range(Höhe_in_Blöcken): # um den gesamten Rand von oben nach unten zu malen
            Stein_malen(-1*(i+1),j,MITTELGRAU,Blockhöhe,Abgerundete_Ecken)
            Stein_malen(Breite_Spielfeld+i,j,MITTELGRAU,Blockhöhe,Abgerundete_Ecken)
    for i in range(Breite_Spielfeld): #unterer Rand
        Stein_malen(i,Höhe_in_Blöcken-2,MITTELGRAU,Blockhöhe,Abgerundete_Ecken)
        Stein_malen(i,Höhe_in_Blöcken-1,MITTELGRAU,Blockhöhe,Abgerundete_Ecken)
    #endregion Rand aufbauen

    #region Menü
    if Level == "Menue":
        #Buttons erstellen
        if Neu_im_Level or Resize:
            L_Texte = ["Start","Trick-Level","Spiel beenden"]
            L_Buttons = Menü_erstellen(1.5,8,Breite_Spielfeld-3,Höhe_in_Blöcken-13,MITTELGRAU, Schriftfarbe2,L_Texte)
            Neu_im_Level = False
            Resize = False

        #Überschrift
        font = Schrift_laden(int(Blockhöhe*2))
        surface = font.render("Tetris",True, Schriftfarbe1)
        Text_x,Text_y = Koordinaten_zu_Pixelposition(Breite_Spielfeld/2,4)
        screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))
        #Buttons klicken
        Geklickt = None
        for B in L_Buttons:
            if B.rect.collidepoint(mx,my):
                Geklickt = B.text
        if Geklickt == "Start":
            Level = "Speed-Level"
            Neu_im_Level = True
        elif Geklickt == "Trick-Level":
            Level = "Trick-Level"
            Level_Nr = 1
            Neu_im_Level = True
        elif Geklickt == "Spiel beenden":
            running = False
        #Buttons malen
        else:
            for B in L_Buttons:
                B.malen()

    #endregion Menü

    #region Level
    if Level == "Speed-Level" or Level == "Trick-Level":
        
        #Variablen zurücksetzen
        if Neu_im_Level:
            if Level == "Speed-Level":
                Liste_Spielfeld = [[None for i in range(Breite_Spielfeld)] for j in range(Höhe_in_Blöcken-2)]
                Level_Nr = 1
                Speed = 1/15
            if Level == "Trick-Level":
                Level_Path = str(fileDirectory) + "/Level_" + str(Level_Nr) + ".txt"
                Liste_Spielfeld = []
                Liste_Farben = [TUERKIS,GELB,BLAU,BRAUN1,ROT,GRUEN,LILA]
                with open(Level_Path,"r") as File:
                    for Line in File:
                        Zeichen = Line.strip()
                        Liste_Zeile = []
                        for x in Zeichen:
                            if x == "N":
                                Liste_Zeile.append(None)
                            if x == "B":
                                i = random.randint(0,len(Liste_Farben)-1)
                                Liste_Zeile.append(Liste_Farben[i])
                        Liste_Spielfeld.append(Liste_Zeile)
                Speed = 1/15
            Nächste_Formen = []
            for i in range(3):
                tmp = random.randint(0,len(Liste_Formen)-1)
                Nächste_Formen.append(Liste_Formen[tmp])
            Neue_Form_benötigt = True
            Zeit_Zeilen_anzeigen = 10
            Es_gibt_fertige_Zeilen = False
            Punkte = 0
            Punktezuwachs = 0
            Timer_Punktezuwachs = 0
            Zeilen = 0
            Level_up = False
            K_down = False
            Neu_im_Level = False
            Verloren = False
            Level_done = False
        
        if not Verloren and not Level_done: #Dinge, die nur passieren sollen, solange Spiel noch nicht verloren ist
            #Neue Figur erstellen
            if Neue_Form_benötigt:
                Aktive_Form = Figur(Breite_Spielfeld/2-1,-1,Nächste_Formen.pop(0))
                tmp = random.randint(0,len(Liste_Formen)-1)
                Nächste_Formen.append(Liste_Formen[tmp])
                Zeit_am_Boden = 10
                Neue_Form_benötigt = False
            
            #Figur drehen & verschieben
            Schneller = False #Beschleunigung durch Tastendurck zurücksetzen
            if K_links:
                if verschieben_möglich(Aktive_Form,Liste_Spielfeld,-1):
                    Aktive_Form.x -= 1
            if K_rechts:
                if verschieben_möglich(Aktive_Form,Liste_Spielfeld,1):
                    Aktive_Form.x += 1
            if K_up:
                Aktive_Form.liste = Aktive_Form.drehen(Liste_Spielfeld)

            #Figur fällt
            Mögliche_Fallhöhe = Fallmöglichkeit(Aktive_Form,Liste_Spielfeld)
            if Mögliche_Fallhöhe > 0:
                Aktive_Form.malen()
                Aktive_Form.schatten(Mögliche_Fallhöhe) #Schatten zeichnen
                if K_down: # Beschleunigung durch Pfeiltaste nach unten
                    Aktive_Form.y += 1
                else:
                    Aktive_Form.y += Speed           
            else: 
                if Aktive_Form.y == -1:
                    Verloren = True
                    Neu_im_Level = True
                if Zeit_am_Boden > 0:
                    Aktive_Form.malen()
                    Zeit_am_Boden -= 1
                else:
                    Liste_Spielfeld = Aktive_Form.in_Liste(Liste_Spielfeld)
                    Neue_Form_benötigt = True

            #Auswertung
            if not Es_gibt_fertige_Zeilen: # fertige Zeilen werden neu entdeckt
                Zeilen_gelöst = Lösen(Liste_Spielfeld)
                if len(Zeilen_gelöst) > 0:
                    Punktezuwachs = 0
                    Timer_Punktezuwachs = 20
                    Level_up = False
                    Es_gibt_fertige_Zeilen = True
                    Zeit_Zeilen_anzeigen = 20
                    for Zeile in Zeilen_gelöst: # Zeilen einfärben
                        for i in range(len(Liste_Spielfeld[0])):
                            Liste_Spielfeld[Zeile][i] = DUNKELGRUEN
                    if len(Zeilen_gelöst) == 1: # Punktezuwachs ermitteln
                        Punktezuwachs = 10
                        Zeilen += 1
                    elif len(Zeilen_gelöst) == 2:
                        Punktezuwachs = 30
                        Zeilen += 2
                    elif len(Zeilen_gelöst) == 3:
                        Punktezuwachs = 50
                        Zeilen += 3
                    elif len(Zeilen_gelöst) == 4:
                        Punktezuwachs = 80
                        Zeilen += 4
                    Punkte += Punktezuwachs
                    if Level == "Speed-Level" and Punkte/100 > Level_Nr:
                        Level_Nr += 1
                        Speed += 1/30
                        Level_up = True
                    if Level == "Trick-Level" and Punkte >= 300:
                        Level_done = True
                        Neu_im_Level = True

            elif Zeit_Zeilen_anzeigen > 0: # es gibt fertige Zeilen, Ticker läuft noch
                Zeit_Zeilen_anzeigen -= 1
            else: # Es gibt fertige Zeilen, ticker abgelaufen
                for Zeile in Zeilen_gelöst: # Zeilen entfernen
                    Liste_Spielfeld.pop(Zeile)
                    Liste_Spielfeld.insert(0,[None for i in range(len(Liste_Spielfeld[0]))])
                Es_gibt_fertige_Zeilen = False
            if Timer_Punktezuwachs > 0: #Punktezuwachs drucken
                font = Schrift_laden(int(Blockhöhe*8/10))
                surface = font.render(f"+ {Punktezuwachs}",True, Schriftfarbe1)
                Text_x,Text_y = Koordinaten_zu_Pixelposition(Breite_Spielfeld/2,5)
                screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))
                if Level_up:
                    font = Schrift_laden(int(Blockhöhe*8/10))
                    surface = font.render("Level up!",True, Schriftfarbe1)
                    Text_x,Text_y = Koordinaten_zu_Pixelposition(Breite_Spielfeld/2,7)
                    screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))
                Timer_Punktezuwachs -= 1

        #region Feld & Umfeld malen

        #Feld malen
        Liste_Spielfeld_malen(Liste_Spielfeld,Blockhöhe,Abgerundete_Ecken)

        #nächste Steine malen
        R_x,R_y = Koordinaten_zu_Pixelposition(Breite_Spielfeld+2,4)
        R = pygame.Rect(R_x,R_y,6*Blockhöhe,11*Blockhöhe)
        pygame.draw.rect(screen,HELLGRAU,R)
        Nachfolger1 = Figur(Breite_Spielfeld+6,7,Nächste_Formen[0])
        Nachfolger2 = Figur(Breite_Spielfeld+6,10,Nächste_Formen[1])
        Nachfolger3 = Figur(Breite_Spielfeld+6,13,Nächste_Formen[2])
        Nachfolger1.x -= Nachfolger1.breite/2
        Nachfolger2.x -= Nachfolger2.breite/2
        Nachfolger3.x -= Nachfolger3.breite/2
        Nachfolger1.malen()
        Nachfolger2.malen()
        Nachfolger3.malen()
        font = Schrift_laden(int(Blockhöhe*8/10))
        surface = font.render("Nachfolger",True, Schriftfarbe1)
        Text_x,Text_y = Koordinaten_zu_Pixelposition(Breite_Spielfeld+5,5)
        screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))

        #Punkte Hintergrund
        R_x,R_y = Koordinaten_zu_Pixelposition(-8,4)
        R = pygame.Rect(R_x,R_y,6*Blockhöhe,3*Blockhöhe)
        pygame.draw.rect(screen,HELLGRAU,R)
        #Punkte Beschriftung
        surface = font.render("Punkte",True, Schriftfarbe1)
        Text_x,Text_y = Koordinaten_zu_Pixelposition(-5,5)
        screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))
        #Punktestand
        surface = font.render(str(Punkte),True, Schriftfarbe2)
        Text_x,Text_y = Koordinaten_zu_Pixelposition(-5,6)
        screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))
        #Level Hintergrund
        R_x,R_y = Koordinaten_zu_Pixelposition(-8,8)
        R = pygame.Rect(R_x,R_y,6*Blockhöhe,3*Blockhöhe)
        pygame.draw.rect(screen,HELLGRAU,R)
        #Level Beschriftung
        surface = font.render("Level",True, Schriftfarbe1)
        Text_x,Text_y = Koordinaten_zu_Pixelposition(-5,9)
        screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))
        #Levelanzeige
        surface = font.render(str(Level_Nr),True, Schriftfarbe2)
        Text_x,Text_y = Koordinaten_zu_Pixelposition(-5,10)
        screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))
        #Reihen Hintergrund
        R_x,R_y = Koordinaten_zu_Pixelposition(-8,12)
        R = pygame.Rect(R_x,R_y,6*Blockhöhe,3*Blockhöhe)
        pygame.draw.rect(screen,HELLGRAU,R)
        #Reihen Beschriftung
        surface = font.render("Reihen",True, Schriftfarbe1)
        Text_x,Text_y = Koordinaten_zu_Pixelposition(-5,13)
        screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))
        #Reihenzähler
        surface = font.render(str(Zeilen),True, Schriftfarbe2)
        Text_x,Text_y = Koordinaten_zu_Pixelposition(-5,14)
        screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))

        #endregion Feld & Umfeld malen

        if Verloren or Level_done:
            #grauer Rahmen
            for i in range(Breite_Spielfeld): #grauer Rahmen
                Stein_malen(i,3,MITTELGRAU,Blockhöhe,Abgerundete_Ecken)
                Stein_malen(i,15,MITTELGRAU,Blockhöhe,Abgerundete_Ecken)
            #Hintergrund
            R_x,R_y = Koordinaten_zu_Pixelposition(-1,4)
            R = pygame.Rect(R_x,R_y,(Breite_Spielfeld+2)*Blockhöhe,11*Blockhöhe)
            pygame.draw.rect(screen,HELLGRAU,R)
            #Buttons erstellen
            if Neu_im_Level or Resize:
                if Verloren:
                    L_Texte = ["Nochmal!","Hauptmenü","Spiel beenden"]
                    L_Buttons = Menü_erstellen(1.5,7,Breite_Spielfeld-3,Höhe_in_Blöcken-14,MITTELGRAU,Schriftfarbe2,L_Texte)
                    Neu_im_Level = False
                    Resize = False
                if Level_done:
                    L_Texte = ["Nächstes Level","Hauptmenü","Spiel beenden"]
                    L_Buttons = Menü_erstellen(1.5,7,Breite_Spielfeld-3,Höhe_in_Blöcken-14,MITTELGRAU,Schriftfarbe2,L_Texte)
                    Neu_im_Level = False
                    Resize = False
            #Text 
            font = Schrift_laden(int(Blockhöhe*0.8))
            if Verloren:    
                Points_str = str(f"Du hast {Punkte} Punkte erreicht.")
                surface = font.render(Points_str,True, Schriftfarbe1)
                Text_x,Text_y = Koordinaten_zu_Pixelposition(Breite_Spielfeld/2,5.5)
                screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))
            if Level_done:    
                Points_str = str(f"{Level_Nr}. Tricklevel geschafft!")
                surface = font.render(Points_str,True, Schriftfarbe1)
                Text_x,Text_y = Koordinaten_zu_Pixelposition(Breite_Spielfeld/2,5.5)
                screen.blit(surface,(Text_x-surface.get_width()/2,Text_y-surface.get_height()/2))
            #Buttons klicken
            Geklickt = None
            for B in L_Buttons:
                if B.rect.collidepoint(mx,my):
                    Geklickt = B.text
            if Geklickt == "Nochmal!":
                Neu_im_Level = True
            if Geklickt == "Nächstes Level":
                Level = "Trick-Level"
                Level_Nr += 1
                Neu_im_Level = True
            if Geklickt == "Hauptmenü":
                Level = "Menue"
                Neu_im_Level = True
            elif Geklickt == "Spiel beenden":
                running = False
            #Buttons malen
            else:
                for B in L_Buttons:
                    B.malen()

    #endregion Level

    #region Spielende
    pygame.display.update()
    clock.tick(30)
pygame.quit()
    #endregion Spielende

#endregion Spiel
