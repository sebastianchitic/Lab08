from database.consumo_DAO import ConsumoDAO
from database.impianto_DAO import ImpiantoDAO
from model.impianto_DTO import Impianto

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        media_mese = []
        for impianto in ImpiantoDAO.get_impianti():
                consumi = impianto.get_consumi()
                somma_kwh_mese = 0
                numero_giorni_mese = 0
                for consumo in consumi:
                    if consumo.data.month == mese:
                        somma_kwh_mese += consumo.kwh
                        numero_giorni_mese += 1
                media_calcolata = 0
                if numero_giorni_mese > 0:
                    media_calcolata = somma_kwh_mese / numero_giorni_mese
                    media_calcolata_rounded = round(media_calcolata, 2)
                media_mese.append((impianto.nome, media_calcolata_rounded))
        return media_mese


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        if giorno == 8:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        for impianto in self._impianti:
            costo_spostamento = 0
            if ultimo_impianto is not None and impianto.id != ultimo_impianto:
                costo_spostamento = 5
            costo_energia = consumi_settimana[impianto.id][giorno-1]
            nuovo_costo = costo_corrente + costo_spostamento + costo_energia
            if nuovo_costo > self.__costo_ottimo and self.__costo_ottimo != -1:
                continue
            sequenza_parziale.append(impianto.id)
            self.__ricorsione(sequenza_parziale,
                             giorno + 1,
                             impianto.id,
                             nuovo_costo,
                             consumi_settimana
            )
            sequenza_parziale.pop()




    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        consumi_prima_settimana = {}
        for impianto in self._impianti:
            consumi_prima_settimana[impianto.id] = []
            consuumi = impianto.get_consumi()
            if consuumi:
                consuumi.sort(key=lambda consumo: consumo.data)
                for consumo in consuumi:
                    if consumo.data.month == mese and consumo.data.day <= 7:
                        consumi_prima_settimana[impianto.id].append(consumo.kwh)
        return consumi_prima_settimana





