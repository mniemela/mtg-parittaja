# -*- coding: latin-1 -*-
import mwmatching
import random
from math import log, pow, ceil
from random import shuffle


def haeSeating(pelaajat, seating1, seating2):
    for p in pelaajat:
        if p.seating == seating1 or p.seating == seating2:
            return p
    return Pelaaja("**Bye**")

class Turnaus:
    """Turnauksen tiedot"""
    
    def __init__(self, nimi_):
        self.nimi = nimi_
        self.kierros = 0
        self.max_kierrokset = 0
        self.pelaajat = {}
        self.matsit = []
        self.bye = Pelaaja("**Bye**")
        self.seatingsit = False
        self.single_elimination = False
        self.draft = False
    def standings(self):
        output = "Rank   Score  Player name              OMW       GW        OGW" + '\n'
        temp = ""
        rank = 1
        #otetaan standingsien mukaan sortattu lista pelaajista
        for p in sorted(self.pelaajat.itervalues()):
            temp = str(rank)
            omw = "{0:.2f}".format(p.omw)
            gw = "{0:.2f}".format(p.gw)
            ogw = "{0:.2f}".format(p.ogw)
            score = str(p.score())
            output += (str(rank) + '.'  + ' ' * (6 - len(temp)) + score +
                ' ' * (7 - len(score)) + 
                p.nimi + ' ' * (25 - len(p.nimi)) + omw + ' ' * (10 - len(omw)) + 
                gw + ' ' * (10 - len(gw)) + ogw + ' ' * (10 - len(ogw)) + '\n')
            rank += 1
        return output
        
    def seatings(self):
        s = range(len(self.pelaajat))
        for p in self.pelaajat.itervalues():
            p.seating = s.pop(random.randint(0, len(s) - 1)) + 1
        self.seatingsit = True
        
    def paritaEliminaatio(self):
        kierros_pelaajat = []
        for p in self.pelaajat.itervalues():
            if p.dropped:
                continue
            else:
                kierros_pelaajat.append(p)
        if not self.draft:
            #haetaan lähin 2:n potenssi, kaava ei kuitenkaan toimi jos pelaajia alle 2
            lukum = pow(2, ceil(log(len(kierros_pelaajat), 2)))
            if lukum < 2:
                lukum = 2
            while lukum > len(kierros_pelaajat):
                kierros_pelaajat.append(Pelaaja("**Bye**"))
            shuffle(kierros_pelaajat)
            while len(kierros_pelaajat) > 0:
                self.matsit.append(Matsi(kierros_pelaajat.pop(), kierros_pelaajat.pop()))
        elif self.kierros == 3:
            while 2 > len(kierros_pelaajat):
                kierros_pelaajat.append(Pelaaja("**Bye**"))
            self.matsit.append(Matsi(kierros_pelaajat.pop(), kierros_pelaajat.pop()))
        elif self.kierros == 2:
            self.matsit.append(Matsi(haeSeating(kierros_pelaajat, 1, 5), haeSeating(kierros_pelaajat, 3, 7)))
            self.matsit.append(Matsi(haeSeating(kierros_pelaajat, 2, 6), haeSeating(kierros_pelaajat, 4, 8)))
        elif self.kierros == 1:
            self.matsit.append(Matsi(haeSeating(kierros_pelaajat, 1, -1), haeSeating(kierros_pelaajat, 5, -1)))
            self.matsit.append(Matsi(haeSeating(kierros_pelaajat, 3, -1), haeSeating(kierros_pelaajat, 7, -1)))
            self.matsit.append(Matsi(haeSeating(kierros_pelaajat, 2, -1), haeSeating(kierros_pelaajat, 6, -1)))
            self.matsit.append(Matsi(haeSeating(kierros_pelaajat, 4, -1), haeSeating(kierros_pelaajat, 8, -1)))

                
    def parita(self):
        self.kierros += 1
        #jos single elimination, paritetaan sillä tavalla
        if self.single_elimination:
            self.paritaEliminaatio()
            return
        viimeinen = self.kierros == self.max_kierrokset
        kierros_pelaajat = []
        #otetaan kierroksella mukana olevat pelaajat standingsien
        #mukaisessa järjestyksessä listaan
        score = -1
        bracket = []
        i = 0
        for p in sorted(self.pelaajat.itervalues()):
            if p.dropped:
                continue
            elif score != p.score():
                i += 1
                bracket.append(i)
                kierros_pelaajat.append(p)
                score = p.score()
            else:
                kierros_pelaajat.append(p)
                bracket.append(i)
        #jos pariton määrä pelaajia, lisätään bye
        if len(kierros_pelaajat) % 2 == 1:
            kierros_pelaajat.append(self.bye)
            bracket.append(i)
        edges = []
        weights = [x for x in range((len(kierros_pelaajat)**2 -
            len(kierros_pelaajat)) / 2)]
        i = 0
        #Jos on edetty 'matriisin' diagonaalille (eli ollaan pelaajan
        #itsensä kohdalla), hypätään seuraavaan sarakkeeseen. Jo pelanneiden painoarvo on 0. 
        #Score-erotuksesta saa penaltyä painoarvoon.
        
        if not viimeinen:
            for p in kierros_pelaajat:
                j = 0
                for r in kierros_pelaajat:
                    if p.nimi == r.nimi:
                        break
                    elif p.onkoPelannut(r):
                        edges.append((i, j, 0))
                        weights.pop()
                    #Byen menemiseen korkeampaan brackettiin isompi penalty kuin
                    #normaaliin down/uppairaukseen
                    elif p.nimi == "**Bye**" or r.nimi == "**Bye**":
                        edges.append((i, j, 200000 - abs(bracket[i] - bracket[j])**2 * 
                            6000 - weights.pop(random.randint(0, len(weights) - 1))))
                    else:
                        edges.append((i, j, 200000 - abs(bracket[i] - bracket[j])**2 * 
                            2000 - weights.pop(random.randint(0, len(weights) - 1))))
                    j += 1
                i += 1
        #täällä käydään läpi pelaajat, lisääminen aloitetaan kun on päästy pelaajasta
        #itsestään yli, seuraavalle standingeissä jota vastaan voi pelata annetaan parempi paino.
        else:
            paired = [False for x in range(len(kierros_pelaajat))]
            for p in kierros_pelaajat:
                j = i
                for r in kierros_pelaajat[i:]:
                    if p.nimi == r.nimi:
                        j += 1
                    elif p.onkoPelannut(r):
                        edges.append((j, i, 0))
                        j += 1
                        weights.pop()
                    elif not paired[i] and not paired[j]:
                        paired[i] = True
                        paired[j] = True
                        edges.append((j, i, 200000 - weights.pop(random.randint(0, len(weights) - 1))))
                        j += 1
                    else:
                        edges.append((j, i, 150000 - weights.pop(random.randint(0, len(weights) - 1))))
                        j += 1
                i += 1

                    
        tulos = mwmatching.maxWeightMatching(edges)
        i = 0
        kaytetty = []
        #lisätään matsit, jos on jo lisättynä niin jatketaan
        for p in tulos:
            if i in kaytetty:
                i += 1
                continue
            self.matsit.append(Matsi(kierros_pelaajat[i], kierros_pelaajat[p]))
            kaytetty.append(p)
            i += 1
            
    def lopetaKierros(self):
        for p in self.matsit:
            p.pelaaja1.tulos(p.win1, p.win2, p.draws, p.pelaaja2)
            p.pelaaja2.tulos(p.win2, p.win1, p.draws, p.pelaaja1)
            if self.single_elimination and p.win1 > p.win2:
                p.pelaaja2.dropped = True
                p.pelaaja2.round_dropped = self.kierros - 1
            elif self.single_elimination and p.win2 > p.win1:
                p.pelaaja1.dropped = True
                p.pelaaja1.round_dropped = self.kierros - 1
                #koska kierros muuttuu parituksen alussa eikä lopussa, joutuu vähentämään yhden
        for p in self.pelaajat.itervalues():
            p.omwogw()
        self.matsit = []
        
    def lisaaPelaaja(self, nimi):
        if nimi in self.pelaajat:
            raise OmaPoikkeus('Pelaajaa ei ole')
        elif nimi == "**Bye**":
            raise OmaPoikkeus('Voi olla vain yksi Bye!')
        else:
            self.pelaajat[nimi] = Pelaaja(nimi)
    
    def pelaajanSeating(self, nimi):
        if nimi in self.pelaajat:
            return self.pelaajat[nimi].seating
        else:
            print "Ei ole"
            raise OmaPoikkeus('Pelaajaa ei ole')
    
    def paivitaPelaaja(self, nimi, uusinimi, dropannut):
        if nimi != uusinimi and uusinimi in self.pelaajat:
            raise OmaPoikkeus('Samanniminen pelaaja on olemassa')
        elif uusinimi == "**Bye**":
            raise OmaPoikkeus('Voi olla vain yksi Bye!')
        elif nimi not in self.pelaajat:
            raise OmaPoikkeus('Pelaajaa ei ole')
        else:
            if dropannut:
                self.pelaajat[nimi].round_dropped = self.kierros
            else:
                self.pelaajat[nimi].round_dropped = -1
            self.pelaajat[nimi].nimi = uusinimi
            self.pelaajat[nimi].dropped = dropannut
            self.pelaajat[uusinimi] = self.pelaajat.pop(nimi)

    def poistaPelaaja(self, nimi):
        if nimi in self.pelaajat:
            del self.pelaajat[nimi]
            return True
        else:
            return False
    
    def onkoDropannut(self, nimi):
        if nimi in self.pelaajat:
            return self.pelaajat[nimi].dropped
        else:
            raise OmaPoikkeus("Pelaajaa ei ole")
    
    #palauttaa matsin, ei saa yli-indeksoida
    def annaMatsi(self, index):
        return self.matsit[index]
        
    def kaikkiPelattu(self):
        pelattu = True
        for m in self.matsit:
            if m.pelattu == False:
                pelattu = False
        return pelattu

class OmaPoikkeus(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
            
class Matsi:
    """Matsin tiedot"""
    
    def __init__(self, pelaaja1_, pelaaja2_):
        self.pelaaja1 = pelaaja1_
        self.pelaaja2 = pelaaja2_
        self.win1 = 0
        self.win2 = 0
        self.draws = 0
        self.pelattu = False
        if pelaaja1_.nimi == "**Bye**":
            self.win2 = 2
            self.pelattu = True
        elif pelaaja2_.nimi == "**Bye**":
            self.win1 = 2
            self.pelattu = True
            
    def tulos(self, win1_, win2_, draws_, pelattu_):
        self.win1 = win1_
        self.win2 = win2_
        self.draws = draws_
        self.pelattu = pelattu_
        
    def annaPelaajat(self): 
        return [self.pelaaja1.nimi, self.pelaaja2.nimi] 
        
    def otsikko (self):
        if not self.pelattu:
            return (self.pelaaja1.nimi + ' ' * (25 - len(self.pelaaja1.nimi)) 
                + '-         ' + self.pelaaja2.nimi)
        else:
            return (self.pelaaja1.nimi + ' ' * (25 - len(self.pelaaja1.nimi)) 
                + '-         ' + self.pelaaja2.nimi + ' ' * (25 - len(self.pelaaja2.nimi))
                + str(self.win1) + '  -  ' + str(self.win2)) + '  -  ' + str(self.draws)
        
        


class Pelaaja:
    """Pelaajan tiedot"""
    
    def __init__(self, nimi_):
        self.nimi = nimi_
        self.voitetut_matsit = 0
        self.tasurit_matsit = 0
        self.voitetut_pelit = 0
        self.pelatut_pelit = 0
        self.tasurit_pelit = 0
        self.vastustajat = []
        self.gw = 0
        self.mw = 0
        self.omw = 0
        self.ogw = 0
        self.dropped = False
        self.seating = 0
        self.round_dropped = -1
        
    def gwmw(self):
        if self.pelatut_pelit > 0:
            temp = (float(3 * self.voitetut_pelit + self.tasurit_pelit) / 
                float(self.pelatut_pelit * 3))
            if temp > 0.33:
                self.gw = temp
            else:
                self.gw = 0.33
        else:
            self.gw = 0
        if len(self.vastustajat) > 0:
            temp = (float(3 * self.voitetut_matsit + self.tasurit_matsit) /
                float(len(self.vastustajat) * 3))
            if temp > 0.33:
                self.mw = temp
            else:
                self.mw = 0.33
        else:
            self.mw = 0
    
    def omwogw(self):
        tulos1 = 0.0
        tulos2 = 0.0
        kierros = float(len(self.vastustajat))
        if kierros == 0:
            self.omw = 0
            self.ogw = 0
            return
        for p in self.vastustajat:
            tulos1 += p.mw
            tulos2 += p.gw
        self.omw = tulos1 / kierros
        self.ogw = tulos2 / kierros
        
    def onkoPelannut(self, pelaaja):
        for p in self.vastustajat:
            if p.nimi == pelaaja.nimi:
                return True
        return False
        
    def tulos(self, win, lose, draw, vastustaja):
        self.voitetut_pelit += win
        self.pelatut_pelit += (lose + win + draw)
        self.tasurit_pelit += draw
        self.vastustajat.append(vastustaja)
        if win > lose:
            self.voitetut_matsit += 1
        elif win == lose:
            self.tasurit_matsit += 1
        self.gwmw()
        
    def score(self):
        return 3 * self.voitetut_matsit + self.tasurit_matsit
        
    #__cmp__:tä ei ole python 3:ssa ja en saanut total_orderingia
    #toimimaan omalla koneella niin joutui luettelemaan kaikki 
    def __eq__(self, other):
        return ((self.score(), self.omw, self.gw, self.ogw) == 
            (other.score(), other.omw, other.gw, other.ogw))
    def __lt__(self, other):
        return ((self.score(), self.omw, self.gw, self.ogw) > 
            (other.score(), other.omw, other.gw, other.ogw))
    def __le__(self, other):
        return ((self.score(), self.omw, self.gw, self.ogw) >=
            (other.score(), other.omw, other.gw, other.ogw))
    def __ne__(self, other):
        return ((self.score(), self.omw, self.gw, self.ogw) !=
            (other.score(), other.omw, other.gw, other.ogw))
    def __ge__(self, other):
        return ((self.score(), self.omw, self.gw, self.ogw) <=
            (other.score(), other.omw, other.gw, other.ogw))
    def __gt__(self, other):
        return ((self.score(), self.omw, self.gw, self.ogw) <
            (other.score(), other.omw, other.gw, other.ogw))