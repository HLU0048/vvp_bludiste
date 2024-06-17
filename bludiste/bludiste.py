import numpy as np
import csv
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from collections import deque
import random


class Bludiste:
    def __init__(self) -> None:
        self._matice = None
        self._incidencni_matice = None
        self._vrcholy = None
        self._vrchol_idx = None
        self._velikost_m = -1
        self._velikost_n = -1
        self._cesta = None

    def nacitani_csv(self, cesta_k_souboru):
        """
        Funkce nacita matici s True/False hodnotami z csv souboru
        """
        with open(cesta_k_souboru, 'r') as csvsoubor:
            soubor = csv.reader(csvsoubor)
            matice_bludiste = []
            for radek in soubor:
                matice_bludiste.append([1 if cell == '1' else 0 for cell in radek])
            self._matice = np.array(matice_bludiste)
            self._velikost_m, self._velikost_n = self._matice.shape

        return 1

    def generovani_bludiste_sablona(self, sablona, velikost) -> None:
        """
        Funkce generuje nahodne pruchozi bludiste na zaklade sablony
        """
        self._matice = sablona.reshape(velikost, velikost)
        self._velikost_m, self._velikost_n = self._matice.shape
        start = (0, 0)
        konec = (self._velikost_m - 1, self._velikost_n - 1)

        # Nyní přidáme náhodné překážky
        for i in range(self._velikost_m):
            for j in range(self._velikost_n):
                if self._matice[i, j] == 1:
                    self._matice[i, j] = 1
                if random.random() < 0.3:
                    self._matice[i, j] = 1

        # Vytvoříme průchozí cestu od startu k cíli
        aktualni = start
        self._matice[aktualni] = 0

        while aktualni != konec:
            sousedi = []
            if aktualni[0] + 1 < self._velikost_m:
                sousedi.append((aktualni[0] + 1, aktualni[1]))
            if aktualni[1] + 1 < self._velikost_n:
                sousedi.append((aktualni[0], aktualni[1] + 1))

            dalsi = random.choice(sousedi)
            self._matice[dalsi] = 0
            aktualni = dalsi

        # Ujistíme se, že start a end jsou průchozí
        self._matice[start] = 0
        self._matice[konec] = 0

    def transformace_na_incidencni_matici(self) -> None:
        """
        Funkce vytvari incidencni matici
        """
        # self._size nahradit
        self._velikost_m, self._velikost_n = self._matice.shape
        vrcholy = []
        hrany = []

        # Najít všechny průchozí vrcholy
        for i in range(self._velikost_m):
            for j in range(self._velikost_n):
                if self._matice[i, j] == 0:  # 0 znamená průchozí buňka
                    vrcholy.append((i, j))
                    # Přidat hrany pro sousední vrcholy
                    if i < self._velikost_m - 1 and self._matice[i + 1, j] == 0:
                        hrany.append(((i, j), (i + 1, j)))
                    if j < self._velikost_n - 1 and self._matice[i, j + 1] == 0:
                        hrany.append(((i, j), (i, j + 1)))

        vrchol_idx = {vrchol: idx for idx, vrchol in enumerate(vrcholy)}
        incidencni_matice = np.zeros((len(vrcholy), len(hrany)), dtype=int)

        for hrana_idx, (v1, v2) in enumerate(hrany):
            incidencni_matice[vrchol_idx[v1], hrana_idx] = 1
            incidencni_matice[vrchol_idx[v2], hrana_idx] = 1
        self._incidencni_matice = incidencni_matice
        self._vrcholy = vrcholy
        self._vrchol_idx = vrchol_idx

    def najdi_nejkratsi_cestu(self, start=(0, 0), konec=(-1, -1)) -> bool:
        """
        Funkce hleda nejkratsi cestu v bludisti na zaklade BFS algoritmu
        """
        if konec == (-1, -1):
           konec = (self._velikost_m - 1, self._velikost_n - 1)

        pocet_vrcholu = self._incidencni_matice.shape[0]
        hrany_pocet = self._incidencni_matice.shape[1]
        start_idx = self._vrchol_idx[start]
        konec_idx = self._vrchol_idx[konec]

        queue = deque([start_idx])
        vzdalenosti = {start_idx: [start]}
        navstiveno = set()
        navstiveno.add(start_idx)

        while queue:
            aktualni_idx = queue.popleft()
            if aktualni_idx == konec_idx:
                self._cesta = vzdalenosti[aktualni_idx]
                return True

            for hrana_idx in range(hrany_pocet):
                if self._incidencni_matice[aktualni_idx, hrana_idx] == 1:
                    for vrchol_idx in range(pocet_vrcholu):
                        if vrchol_idx != aktualni_idx and self._incidencni_matice[vrchol_idx, hrana_idx] == 1:
                            if vrchol_idx not in navstiveno:
                                navstiveno.add(vrchol_idx)
                                queue.append(vrchol_idx)
                                vzdalenosti[vrchol_idx] = vzdalenosti[aktualni_idx] + [self._vrcholy[vrchol_idx]]

        return False

    def mark_path_in_maze(self) -> None:
        """
        Pomocna funkce pro lepsi vykresleni cesty v bludisti
        Prevadi nejkratsi cestu na hodnotu 2
        """
        for (i, j) in self._cesta:
            self._matice[i, j] = 2

    def vykresleni_grafu(self):
        """
        Funkce pro vykresleni bludiste s nejkratsi cestou
        """
        cmap = ListedColormap(['white', 'black', 'red'])

        fig = plt.figure(figsize=(5, 5))
        plt.imshow(self._matice, cmap=cmap, interpolation='nearest')
        plt.show()
