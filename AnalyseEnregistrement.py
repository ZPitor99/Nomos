import statistics
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class Enregistrement:
    timestamp: float
    key_code: int
    key_repr: str

class AnalyseEnregistrementbis:
    def __init__(self, data:list[Enregistrement]):
        self.liste_enregistrement = data
        self.patterns = defaultdict(int)
        self.spam_stats = {}
        self.intervales = {}

    def analyse_patterns(self):
        for i in range(len(self.liste_enregistrement) - 1):
            courant = self.liste_enregistrement[i].key_repr
            suivant = self.liste_enregistrement[i + 1].key_repr
            pattern = f"{courant} -> {suivant}"
            self.patterns[pattern] += 1

        # Trier par fréquence décroissante
        patterns_trie = sorted(self.patterns.items(), key=lambda x: x[1], reverse=True)

        print("Top 20 des patterns de touches les plus fréquents:")
        for pattern, count in patterns_trie[:10]:
            print(f"  {pattern}: {count} fois")

        self.patterns = patterns_trie
        return self.patterns

    def analyse_spam_stats(self, longueur_spam_min: int = 3):
        spam_sequences = defaultdict(list)  # touche -> [longueurs des séquences]

        if not self.liste_enregistrement:
            return {}

        courant = self.liste_enregistrement[0].key_repr
        courant_longueur = 1

        for i in range(1, len(self.liste_enregistrement)):
            if self.liste_enregistrement[i].key_repr == courant:
                courant_longueur += 1
            else:
                # Fin de séquence
                if courant_longueur >= longueur_spam_min:
                    spam_sequences[courant].append(courant_longueur)

                courant = self.liste_enregistrement[i].key_repr
                courant_longueur = 1

        # Traiter la dernière séquence
        if courant_longueur >= longueur_spam_min:
            spam_sequences[courant].append(courant_longueur)

        # Calculer les statistiques pour chaque touche spammée
        spam_stats = {}
        for key, sequences in spam_sequences.items():
            if sequences:
                spam_stats[key] = {
                    'nombre_spam': len(sequences),
                    'longueur_moyenne': statistics.mean(sequences),
                    'longueur_mediane': statistics.median(sequences),
                    'plus_longue_serie': max(sequences),
                    'total_appui_durant_spam': sum(sequences)
                }

        # Trier par nombre total d’appuis lors du spam
        spam_trie = sorted(spam_stats.items(),
                             key=lambda x: x[1]['total_appui_durant_spam'],
                             reverse=True)

        print("Top 5 des touches les plus spammées:")
        for i, (key, stats) in enumerate(spam_trie[:5]):
            print(f"  {i + 1}. Touche '{key}':")
            print(f"     - Nombre de séquences de spam: {stats['nombre_spam']}")
            print(f"     - Longueur moyenne: {stats['longueur_moyenne']:.1f} appuis")
            print(f"     - Longueur médiane: {stats['longueur_mediane']:.1f} appuis")
            print(f"     - Plus longue séquence: {stats['plus_longue_serie']} appuis")
            print(f"     - Total d'appuis en spam: {stats['total_appui_durant_spam']}")

        self.spam_stats = spam_stats
        return self.spam_stats

    def analyse_intervales(self, considere_pause: float = 5.0):
        if len(self.liste_enregistrement) < 2:
            return None

        intervals = []
        longue_pauses = 0

        for i in range(len(self.liste_enregistrement) - 1):
            interval = self.liste_enregistrement[i + 1].timestamp - self.liste_enregistrement[i].timestamp

            if interval <= considere_pause:
                intervals.append(interval)
            else:
                longue_pauses += 1

        if not intervals:
            print("Aucun intervalle valide trouvé")
            return None

        avg_interval = statistics.mean(intervals)
        median_interval = statistics.median(intervals)

        print(f"Intervalles analysés: {len(intervals)}")
        print(f"Longues pauses exclues: {longue_pauses}")
        print(f"Écart moyen: {avg_interval:.3f} secondes")
        print(f"Écart médian: {median_interval:.3f} secondes")
        print(f"Écart minimum: {min(intervals):.3f} secondes")
        print(f"Écart maximum: {max(intervals):.3f} secondes")

        self.intervales = {
            'moyen': avg_interval,
            'median': median_interval,
            'min': min(intervals),
            'max': max(intervals),
            'nombre': len(intervals),
            'nb_pause_supprime': longue_pauses
        }
        return self.intervales