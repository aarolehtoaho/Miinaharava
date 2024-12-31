"""
    Miinaharava
    Aaro Lehtoaho
"""
import json
from random import randint
from math import floor, ceil
from datetime import datetime
from numpy import full
from haravasto import grafiikka, lataa_kuvat, luo_ikkuna, tyhjaa_ikkuna, \
        piirra_tausta, piirra_tekstia, aloita_ruutujen_piirto, \
        lisaa_piirrettava_ruutu, piirra_ruudut, aseta_piirto_kasittelija, \
        aseta_hiiri_kasittelija, aloita, lopeta, aseta_toistuva_kasittelija, \
        aseta_nappain_kasittelija, muuta_ikkunan_koko, HIIRI_VASEN, HIIRI_OIKEA

# Vakiot, jotka kuvaavat ruutujen mahdollisia tiloja:
AVATTU_TYHJA, AVATTU_1, AVATTU_2, AVATTU_3, AVATTU_4 = 0, 1, 2, 3, 4
AVATTU_5, AVATTU_6, AVATTU_7, AVATTU_8, AVATTU_MIINA = 5, 6 ,7, 8, 9
SULJETTU_TYHJA, SULJETTU_1, SULJETTU_2, SULJETTU_3 = 10, 11, 12, 13
SULJETTU_4, SULJETTU_5, SULJETTU_6, SULJETTU_7, SULJETTU_8 = 14, 15, 16, 17, 18
SULJETTU_MIINA, LIPPU_TYHJA, LIPPU_1, LIPPU_2, LIPPU_3 = 19, 20, 21, 22, 23
LIPPU_4, LIPPU_5, LIPPU_6, LIPPU_7, LIPPU_8 = 24, 25, 26, 27, 28
LIPPU_MIINA, TILAN_MUUTOS = 29, 10
#(Esim: SULJETTU_2 - TILAN_MUUTOS == AVATTU_2)

FONTTI = "Times New Roman"
PUNAINEN = (255, 0, 0, 255)
VIHREA = (0, 255, 0, 255)
MUSTA = (0, 0, 0, 255)

#Käsittelijäfunktioiden tarvitsemat tiedot
pelin_tiedot = {
    "ruudukko": [],
    "miina_lista": [],
    "ruutu_lista": [],
    "leveys": "",
    "korkeus": "",
    "miinat": "",
    "virheteksti": "",
    "pelin_tila": "valikko",
    "syotteen_tila": "leveys",
    "kelvollinen_syote": True,
    "ensimmainen_avaus": True,
    "aika": 0.0,
    "vuoro": 0,
    "avatut_ruudut": 0,
    "keskikohta_x": 0,
    "ikkunan_korkeus": 0
}

tilastoikkuna = {
    "tilastot": [],#JSON tiedostosta luetut sanakirjat lisätään tähän
    "sivu": 0,#Tilastoikkunassa aukioleva sivu
    "sivut": 1#Sivujen lukumäärä. Yhdelle sivulle mahtuu 15 riviä.
}

def piirra_valikko() -> None:
    """Piirtää valikon, jossa käyttäjä voi valita ruudukon dimensiot sekä miinojen
       määrän ja aloittaa tai sulkea pelin tai katsoa tilastoja."""
    tyhjaa_ikkuna()
    piirra_tausta()
    aloita_ruutujen_piirto()
    korkeus = pelin_tiedot["ikkunan_korkeus"]
    keski = pelin_tiedot["keskikohta_x"]

    piirra_tekstia("Miinantallaaja", keski - 100, korkeus - 100, fontti = FONTTI)
    lisaa_piirrettava_ruutu("x", keski - 150, korkeus - 100)
    lisaa_piirrettava_ruutu("x", keski + 150, korkeus - 100)

    for i in range(5): #aloita nappi
        lisaa_piirrettava_ruutu("0", keski - 100 + i * 40, 50)
    for i in range(2): #lopeta nappi
        lisaa_piirrettava_ruutu("0", keski - 45 + i * 40, 5)
    for i in range(3): #tilastot nappi
        lisaa_piirrettava_ruutu("0", grafiikka["ikkuna"].width - 45 - i * 40, 5)

    sanat = ("Leveys:", "Korkeus:", "Miinat:")
    for i in range(3):
        if pelin_tiedot["syotteen_tila"] == sanat[i].lower()[:-1]:
            lisaa_piirrettava_ruutu("f", 30, korkeus - 150 - i * 50)
        else:
            lisaa_piirrettava_ruutu("x", 30, korkeus - 150 - i * 50)
        syote_teksti = sanat[i] + pelin_tiedot[sanat[i].lower()[:-1]]
        testi_y = korkeus - 145 - i * 50
        piirra_tekstia(syote_teksti, 80, testi_y, fontti = FONTTI, koko = 20)
    piirra_ruudut()

    ohjeteksti = "Kirjoita yläpuolelle ruudukon leveys, korkeus ja miinojen määrä"
    piirra_tekstia(ohjeteksti, 20, korkeus - 300, fontti = FONTTI, koko = 16)
    if not pelin_tiedot["kelvollinen_syote"]:
        piirra_tekstia(pelin_tiedot["virheteksti"], 30, korkeus - 350, PUNAINEN, FONTTI, 30)
    piirra_tekstia("Aloita peli!", keski - 90, 50, VIHREA, FONTTI, 30)
    piirra_tekstia("Lopeta", keski - 40, 10, PUNAINEN, FONTTI, 20)
    piirra_tekstia("Tilastot", grafiikka["ikkuna"].width - 115, 6, VIHREA, FONTTI, 24)

def piirra_peli() -> None:
    """Piirtää pelitilanteen, jossa on ruudukko ja yläpalkki tietoineen"""
    tyhjaa_ikkuna()
    piirra_tausta()

    aloita_ruutujen_piirto()
    ikkunan_korkeus = pelin_tiedot["ikkunan_korkeus"]
    keskikohta_x = pelin_tiedot["keskikohta_x"]
    for rivi in range(int(pelin_tiedot["korkeus"])):
        for sarake in range(int(pelin_tiedot["leveys"])):
            ruutu = pelin_tiedot["ruudukko"][rivi][sarake]
            x, y = sarake * 40, ikkunan_korkeus - 80 - rivi * 40
            if ruutu in range(SULJETTU_TYHJA, SULJETTU_MIINA + 1):
                lisaa_piirrettava_ruutu(" ", x, y)
            elif ruutu == AVATTU_TYHJA:
                lisaa_piirrettava_ruutu("0", x, y)
            elif ruutu == AVATTU_MIINA:
                lisaa_piirrettava_ruutu("x", x, y)
            elif ruutu in range(AVATTU_1, AVATTU_8 + 1):
                lisaa_piirrettava_ruutu(f"{ruutu}", x, y)
            else:
                lisaa_piirrettava_ruutu("f", x, y)
    piirra_ruudut()

    piirra_tekstia(f"Aika: {int(pelin_tiedot['aika'])}", \
                   20, ikkunan_korkeus - 30, MUSTA, FONTTI, 12)
    piirra_tekstia(f"Miinat: {pelin_tiedot['miinat']}", \
                   keskikohta_x - 30, ikkunan_korkeus - 30, MUSTA, FONTTI, 12)
    if pelin_tiedot["pelin_tila"] == "havio":
        piirra_tekstia("HÄVISIT", \
                       keskikohta_x - 80, ikkunan_korkeus // 2 - 30, PUNAINEN, FONTTI, 30)
    elif pelin_tiedot["pelin_tila"] == "voitto":
        piirra_tekstia("VOITIT", \
                       keskikohta_x - 80, ikkunan_korkeus // 2 - 30, VIHREA, FONTTI, 30)

def piirra_tilastot() -> None:
    """Piirtää tilastoikkunan, kun tilastot- nappia painettaessa hiiri_kasittelija()
       asettaa tämän piirtokäsittelijäksi. Näyttää sivulla 15 pelattua peliä kerrallaan
       ja sivu vaihtuu painamalla hiiren vasenta."""
    tyhjaa_ikkuna()
    piirra_tausta()
    tilastot = tilastoikkuna["tilastot"]
    sivu = tilastoikkuna["sivu"]

    if tilastoikkuna["tilastot"] is None:
        piirra_tekstia("Tilastoja ei ole", \
                       5, pelin_tiedot["ikkunan_korkeus"] - 40, MUSTA, FONTTI, 20)
    else:
        sisalto = tilastot[0 + sivu * 15: 19 + sivu * 15]
        for i, tiedot in enumerate(sisalto):
            teksti = f"{tiedot['paivamaara']}: {tiedot['tulos']}, {tiedot['kesto_m']} m "
            teksti += f"{tiedot['kesto_s']} s, {tiedot['klikkaukset']} klikkausta, "
            teksti += f"{tiedot['leveys']} X {tiedot['korkeus']}, {tiedot['miinat']} miinaa."
            piirra_tekstia(teksti, \
                           5, pelin_tiedot["ikkunan_korkeus"] - 40 - i * 40, MUSTA, FONTTI, 20)

def etsi_tyhja_ruutu(x: int, y: int) -> tuple[int, int]:
    """sijoita_miinat() kutsuu tätä funktiota, jos arvotussa ruudussa on jo miina.
       Palauttaa ruudun vierestä seuraavan vapaan ruudun."""
    uusi_x = x
    uusi_y = y
    while True:
        uusi_x += 1
        if uusi_x >= int(pelin_tiedot["leveys"]):
            uusi_x = 0
            uusi_y += 1
            if uusi_y >= int(pelin_tiedot["korkeus"]):
                uusi_y = 0
        if pelin_tiedot["ruudukko"][uusi_y][uusi_x] == SULJETTU_TYHJA:#
            pelin_tiedot["ruudukko"][uusi_y][uusi_x] = SULJETTU_MIINA
            break
    return uusi_x, uusi_y

def luo_ruudukko() -> None:
    """Luo ruudukon valitulle leveydelle ja korkeudelle ja kutsuu
       sijoita_miinat() funktion. Numeroruutujen lisääminen tehdään
       vasta ensimmäisen avauksen jälkeen."""
    pelin_tiedot["ruudukko"] = full((int(pelin_tiedot["korkeus"]), \
                                     int(pelin_tiedot["leveys"])), SULJETTU_TYHJA, int)
    #Sama ilman numpyä:
    #pelin_tiedot["ruudukko"] = [[SULJETTU_TYHJA for i in range(int(pelin_tiedot["leveys"]))] \
                                #for i in range(int(pelin_tiedot["korkeus"]))]
    sijoita_miinat(int(pelin_tiedot["miinat"]))

def avaa_ruutu(x: int, y: int) -> None:
    """Avaa ruudun. Jos se on tyhjä, niin lisätään viereiset ruudut listaan
       ja kutsutaan avaa_tyhja_alue()"""
    if pelin_tiedot["ruudukko"][y][x] > AVATTU_MIINA:
        pelin_tiedot["ruudukko"][y][x] -= TILAN_MUUTOS
        pelin_tiedot["avatut_ruudut"] += 1
    if pelin_tiedot["ruudukko"][y][x] == AVATTU_TYHJA:
        lisaa_viereiset_ruudut(x, y)
        avaa_tyhja_alue()
    elif pelin_tiedot["ruudukko"][y][x] == AVATTU_MIINA:
        pelin_tiedot["pelin_tila"] = "havio"
        kirjaa_tulokset()

def avaa_tyhja_alue() -> None:
    """Käy läpi listaa avattavista ruuduista, kunnes lista tyhjenee. Aukaisee käsiteltävän
       ruudun ja tyhjän ruudun kohdalla lisää sen viereiset tyhjät ruudut listaan"""
    while len(pelin_tiedot["ruutu_lista"]) > 0:
        ruutu = pelin_tiedot["ruutu_lista"].pop()
        x, y = ruutu[0], ruutu[1]
        if on_alueella(x, y):
            if pelin_tiedot["ruudukko"][y][x] == SULJETTU_TYHJA:
                pelin_tiedot["ruudukko"][y][x] -= TILAN_MUUTOS
                pelin_tiedot["avatut_ruudut"] += 1
                lisaa_viereiset_ruudut(x, y)
                continue
            if pelin_tiedot["ruudukko"][y][x] in range(SULJETTU_1, SULJETTU_MIINA + 1):
                avaa_ruutu(x, y)
                continue

def lisaa_viereiset_ruudut(x: int, y: int) -> None:
    """Lisää ruudun (x, y) ympäröivät ruudut listaan vaaka, pysty ja viistosuunnissa"""
    for y_muutos in range(-1, 2):
        for x_muutos in range(-1, 2):
            pelin_tiedot["ruutu_lista"].append((x + x_muutos, y + y_muutos))

def on_alueella(x: int, y: int) -> bool:
    """Tarkistaa ettei käsiteltävä ruutu ole alueen ulkopuolella
       IndexError välttämiseen"""
    sisalla_leveys = 0 <= x <= int(pelin_tiedot["leveys"]) - 1
    sisalla_korkeus = 0 <= y <= int(pelin_tiedot["korkeus"]) - 1
    return sisalla_leveys and sisalla_korkeus

def sijoita_miinat(miinat: int) -> None:
    """Arpoo ruudun ja sijoittaa sen ruudukkoon. Jos valitussa ruudussa on jo miina,
       kutsutaan etsi_tyhja_ruutu() funktiota, joka valitsee viereisen tyhjän ruudun"""
    for _ in range(miinat):
        kohde_x = randint(0, int(pelin_tiedot["leveys"]) - 1)
        kohde_y = randint(0, int(pelin_tiedot["korkeus"]) - 1)
        if not pelin_tiedot["ruudukko"][kohde_y][kohde_x] == SULJETTU_TYHJA:
            kohde_x, kohde_y = etsi_tyhja_ruutu(kohde_x, kohde_y)
        pelin_tiedot["ruudukko"][kohde_y][kohde_x] = SULJETTU_MIINA
        pelin_tiedot["miina_lista"].append((kohde_x, kohde_y))

def sijoita_numerot() -> None:
    """Käy läpi asetetut miinat ja lisää miinan ympäröiviin ruutuihin arvon 1"""
    for (x, y) in pelin_tiedot["miina_lista"]:
        offset_x, offset_y = -1, -1
        while offset_y <= 1:
            if on_alueella(x + offset_x, y + offset_y):
                if pelin_tiedot["ruudukko"][y + offset_y][x + offset_x] != SULJETTU_MIINA:
                    pelin_tiedot["ruudukko"][y + offset_y][x + offset_x] += 1
            offset_x += 1
            if offset_x == 2:
                offset_x = -1
                offset_y += 1

def kasittele_ensimmainen_avaus(x: int, y: int) -> None:
    """Ensimmäinen avaus käsitellään tällä funktiolla, jotta osuminen miinaan
       ei ole mahdollinen. Numeroruutujen asettaminen tapahtuu mahdollisen miinan
       siirron jälkeen"""
    pelin_tiedot["vuoro"] += 1
    ruutu_x, ruutu_y = etsi_ruutu(x, y)
    for miina in pelin_tiedot["miina_lista"]:
        if miina == (ruutu_x, ruutu_y):
            pelin_tiedot["miina_lista"].remove(miina)
            pelin_tiedot["ruudukko"][ruutu_y][ruutu_x] = AVATTU_TYHJA
            pelin_tiedot["avatut_ruudut"] += 1
            sijoita_miinat(1)
    sijoita_numerot()
    avaa_ruutu(ruutu_x, ruutu_y)
    pelin_tiedot["ensimmainen_avaus"] = False

def etsi_ruutu(x: int, y: int) -> tuple[int, int]:
    """Etsii avattavan ruudun sijainnin hiiren sijainnin perusteella"""
    ruutu_x = floor(x / 40)
    ruutu_y = floor((pelin_tiedot["ikkunan_korkeus"] - 40 - y) / 40)
    return ruutu_x, ruutu_y

def hiiri_alueella(x: int, y: int) -> bool:
    """Tarkistaa, että hiiri on ruudukossa, jotta alueen ulkopuolisia
       painalluksia ei käsitellä"""
    raja_x, raja_y = grafiikka["ikkuna"].width, pelin_tiedot["ikkunan_korkeus"] - 40
    if 0 < x < raja_x and 0 < y < raja_y:
        return True
    return False

def tarkista_voitto() -> None:
    """Ruudun avaamisten yhteydessä tarkistetaan onko peli voitettu"""
    ruudut_yhteensa = int(pelin_tiedot["leveys"]) * int(pelin_tiedot["korkeus"])
    miinat = int(pelin_tiedot["miinat"])
    if pelin_tiedot["avatut_ruudut"] == ruudut_yhteensa - miinat:
        if pelin_tiedot["pelin_tila"] != "havio":
            pelin_tiedot["pelin_tila"] = "voitto"
            kirjaa_tulokset()

def kirjaa_tulokset() -> None:
    """Kirjaa tulokset JSON tiedostoon"""
    tiedot = {
        "paivamaara": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tulos": 'Häviö' if pelin_tiedot['pelin_tila'] == 'havio' else 'Voitto',
        "kesto_m": int(pelin_tiedot['aika'] / 60),
        "kesto_s": int(pelin_tiedot['aika'] % 60),
        "klikkaukset": pelin_tiedot['vuoro'],
        "leveys": pelin_tiedot['leveys'],
        "korkeus": pelin_tiedot['korkeus'],
        "miinat": pelin_tiedot['miinat']
    }
    with open("pelihistoria.json", "a", encoding="utf-8") as t:
        json.dump(tiedot, t)
        t.write("\n")

def lue_tilastot() -> list[dict] | None:
    """Lukee 'pelihistoria.json' tiedostosta tilastot ja asettaa jokaisen
       rivin sisältämän sanakirjan palautettavaan listaan."""
    try:
        with open("pelihistoria.json", "r", encoding="utf-8") as t:
            tilastot = [json.loads(rivi) for rivi in t]
            if tilastot == []:
                return None
            return tilastot
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return None

def nollaa_peli() -> None:
    """Palauttaa pelin tiedot alkutilanteeseen. Kutsutaan pelin päätyttyä"""
    pelin_tiedot["pelin_tila"] = "valikko"
    pelin_tiedot["leveys"] = ""
    pelin_tiedot["korkeus"] = ""
    pelin_tiedot["miinat"] = ""
    pelin_tiedot["aika"] = 0.0
    pelin_tiedot["vuoro"] = 0
    pelin_tiedot["avatut_ruudut"] = 0
    pelin_tiedot["ruudukko"] = []
    pelin_tiedot["miina_lista"] = []
    pelin_tiedot["ensimmainen_avaus"] = True

    muuta_ikkunan_koko(800, 600)
    pelin_tiedot["keskikohta_x"] = grafiikka["ikkuna"].width / 2
    pelin_tiedot["ikkunan_korkeus"] = grafiikka["ikkuna"].height
    aseta_piirto_kasittelija(piirra_valikko)

def aloita_peli() -> None:
    """Tarkistaa ehdot pelin aloittamiselle ja sen toteutuessa
       luo ruudukon ja asettaa piirtokäsittelijän."""
    arvot = {
        "leveys": 0,
        "korkeus": 0,
        "miinat": 0
    }
    for i in ("leveys", "korkeus", "miinat"):
        if pelin_tiedot[i] != "":
            arvot[i] = int(pelin_tiedot[i])
    if arvot["leveys"] * arvot["korkeus"] <= arvot["miinat"]:
        pelin_tiedot["kelvollinen_syote"] = False
        if arvot["leveys"] * arvot["korkeus"] == 0:
            pelin_tiedot["virheteksti"] = "Liian pieni alue"
        else:
            pelin_tiedot["virheteksti"] = "Miinat eivät mahdu alueelle"
    elif arvot["leveys"] > 200 or arvot["korkeus"] > 200:
        pelin_tiedot["kelvollinen_syote"] = False
        pelin_tiedot["virheteksti"] = "Alue on liian suuri"
    elif arvot["leveys"] > 0 and arvot["korkeus"] > 0:
        pelin_tiedot["pelin_tila"] = "peli"
        if pelin_tiedot["miinat"] == "":
            pelin_tiedot["miinat"] = "0"

        luo_ruudukko()
        ikkuna_x = int(pelin_tiedot["leveys"]) * 40
        ikkuna_y = (int(pelin_tiedot["korkeus"]) + 1) * 40
        muuta_ikkunan_koko(ikkuna_x, ikkuna_y)
        pelin_tiedot["keskikohta_x"] = grafiikka["ikkuna"].width / 2
        pelin_tiedot["ikkunan_korkeus"] = grafiikka["ikkuna"].height
        aseta_piirto_kasittelija(piirra_peli)

def hiiri_kasittelija(x: int, y: int, nappi: int, modit: int) -> None:
    """Käsittelee hiiren painallukset"""
    # pylint: disable=unused-argument
    if pelin_tiedot["pelin_tila"] == "valikko" and nappi == HIIRI_VASEN:
        hiiren_kasittely_valikossa(x, y)
    elif pelin_tiedot["pelin_tila"] == "peli" and hiiri_alueella(x, y):
        hiiren_kasittely_pelissa(x, y, nappi)
    elif pelin_tiedot["pelin_tila"] == "tilastot" and nappi == HIIRI_VASEN:
        if tilastoikkuna["sivu"] == tilastoikkuna["sivut"] - 1:
            pelin_tiedot["pelin_tila"] = "valikko"
            tilastoikkuna["sivu"] = 0
            aseta_piirto_kasittelija(piirra_valikko)
        else:
            tilastoikkuna["sivu"] += 1
    elif pelin_tiedot["pelin_tila"] == "havio" or \
        pelin_tiedot["pelin_tila"] == "voitto" and nappi == HIIRI_VASEN:
        nollaa_peli()

def hiiren_kasittely_valikossa(x: int, y: int):
    """Käsittelee syötekenttien valinnat sekä aloita-, lopeta-
       ja tilastot- nappien painamisen"""
    keski = pelin_tiedot["keskikohta_x"]
    leveys = grafiikka["ikkuna"].width
    korkeus = pelin_tiedot["ikkunan_korkeus"]

    if korkeus - 150 <= y <= korkeus - 110:
        pelin_tiedot["syotteen_tila"] = "leveys"
    elif korkeus - 200 <= y <= korkeus - 160:
        pelin_tiedot["syotteen_tila"] = "korkeus"
    elif korkeus - 250 <= y <= korkeus - 210:
        pelin_tiedot["syotteen_tila"] = "miinat"
    elif keski - 100 <= x <= keski + 60 and 50 <= y <= 90:
        aloita_peli()
    elif keski - 45 <= x <= keski + 35 and 5 <= y <= 45:
        lopeta()
    elif leveys - 125 <= x <= leveys - 5 and 5 <= y <= 45:
        pelin_tiedot["pelin_tila"] = "tilastot"
        tilastoikkuna["tilastot"] = lue_tilastot()
        if tilastoikkuna["tilastot"] is None:
            tilastoikkuna["sivut"] = 1
        else:
            tilastoikkuna["sivut"] = ceil(len(tilastoikkuna["tilastot"]) / 15)
        aseta_piirto_kasittelija(piirra_tilastot)

def hiiren_kasittely_pelissa(x: int, y: int, nappi: int):
    """Kutsuu ruudun avausfunktiota hiiren vasenta painettaessa ja
       lippujen asettamisen ja poistamisen hiiren oikeaa painettaessa"""
    ruutu_x, ruutu_y = etsi_ruutu(x, y)
    ruutu = pelin_tiedot["ruudukko"][ruutu_y][ruutu_x]
    if nappi == HIIRI_VASEN:
        if pelin_tiedot["ensimmainen_avaus"]:
            kasittele_ensimmainen_avaus(x, y)
        else:
            if ruutu in range(SULJETTU_TYHJA, SULJETTU_MIINA + 1):
                pelin_tiedot["vuoro"] += 1
                avaa_ruutu(ruutu_x, ruutu_y)
        tarkista_voitto()

    elif nappi == HIIRI_OIKEA and not pelin_tiedot["ensimmainen_avaus"]:
        if ruutu in range(SULJETTU_TYHJA, SULJETTU_MIINA + 1):
            pelin_tiedot["ruudukko"][ruutu_y][ruutu_x] += TILAN_MUUTOS
        elif ruutu in range(LIPPU_TYHJA, LIPPU_MIINA + 1):
            pelin_tiedot["ruudukko"][ruutu_y][ruutu_x] -= TILAN_MUUTOS

def nappain_kasittelija(symboli: int, muokkausnapit: int) -> None:
    """Tarvitaan vain pelin alkuvalikossa, jotta kirjoitettuja arvoja voidaan pyyhkiä"""
    # pylint: disable=unused-argument
    if pelin_tiedot["pelin_tila"] == "valikko" and symboli == 65288:# 65288-> BACKSLASH
        kirjoitettava_arvo = pelin_tiedot["syotteen_tila"]
        pelin_tiedot[kirjoitettava_arvo] = pelin_tiedot[kirjoitettava_arvo][:-1]

def kirjoitus_kasittelija(teksti: str) -> None:
    """Kasittelee arvojen kirjoittamisen alkuvalikossa"""
    if pelin_tiedot["pelin_tila"] == "valikko":
        try:
            int(teksti.strip())
        except ValueError:
            pelin_tiedot["kelvollinen_syote"] = False
            pelin_tiedot["virheteksti"] = f"Virheellinen syöte: {teksti}"
        else:
            pelin_tiedot["kelvollinen_syote"] = True

        match pelin_tiedot["syotteen_tila"]:
            case "leveys":
                if pelin_tiedot["kelvollinen_syote"]:
                    pelin_tiedot["leveys"] += teksti
            case "korkeus":
                if pelin_tiedot["kelvollinen_syote"]:
                    pelin_tiedot["korkeus"] += teksti
            case "miinat":
                if pelin_tiedot["kelvollinen_syote"]:
                    pelin_tiedot["miinat"] += teksti

def paivitys_kasittelija(kulunut_aika: float) -> None:
    """Laskee kuluneen ajan pelin ollessa käynnissä"""
    if pelin_tiedot["pelin_tila"] == "peli":
        pelin_tiedot["aika"] += kulunut_aika


if __name__ == "__main__":
    # pylint: disable=missing-docstring,unused-argument
    lataa_kuvat("spritet")
    luo_ikkuna()

    pelin_tiedot["keskikohta_x"] = grafiikka["ikkuna"].width / 2
    pelin_tiedot["ikkunan_korkeus"] = grafiikka["ikkuna"].height

    grafiikka["ikkuna"].on_text = kirjoitus_kasittelija
    aseta_nappain_kasittelija(nappain_kasittelija)
    aseta_piirto_kasittelija(piirra_valikko)
    aseta_hiiri_kasittelija(hiiri_kasittelija)
    aseta_toistuva_kasittelija(paivitys_kasittelija, 1/60)

    aloita()
