-- Fichier: info_sql/statistiques_avancees.sql
-- Statistiques avancées par jour de la semaine
SELECT 
    Format(timestamp, 'dddd') as jour_semaine,
    COUNT(*) as total_frappes,
    AVG(COUNT(*)) OVER() as moyenne_generale
FROM KeyPresses 
WHERE session_id = ?
GROUP BY Format(timestamp, 'dddd')
ORDER BY 
    CASE Format(timestamp, 'dddd')
        WHEN 'lundi' THEN 1
        WHEN 'mardi' THEN 2
        WHEN 'mercredi' THEN 3
        WHEN 'jeudi' THEN 4
        WHEN 'vendredi' THEN 5
        WHEN 'samedi' THEN 6
        WHEN 'dimanche' THEN 7
    END;

-- Fichier: info_sql/analyse_productivite.sql
-- Analyse de productivité par tranche horaire
SELECT 
    CASE 
        WHEN Format(timestamp, 'hh') BETWEEN '08' AND '11' THEN 'Matinée'
        WHEN Format(timestamp, 'hh') BETWEEN '12' AND '13' THEN 'Pause déjeuner'
        WHEN Format(timestamp, 'hh') BETWEEN '14' AND '17' THEN 'Après-midi'
        WHEN Format(timestamp, 'hh') BETWEEN '18' AND '21' THEN 'Soirée'
        ELSE 'Autre'
    END as tranche_horaire,
    COUNT(*) as frappes,
    COUNT(DISTINCT Format(timestamp, 'yyyy-mm-dd')) as nb_jours,
    ROUND(COUNT(*) / COUNT(DISTINCT Format(timestamp, 'yyyy-mm-dd')), 2) as moyenne_par_jour
FROM KeyPresses
WHERE session_id = ?
GROUP BY 
    CASE 
        WHEN Format(timestamp, 'hh') BETWEEN '08' AND '11' THEN 'Matinée'
        WHEN Format(timestamp, 'hh') BETWEEN '12' AND '13' THEN 'Pause déjeuner'
        WHEN Format(timestamp, 'hh') BETWEEN '14' AND '17' THEN 'Après-midi'
        WHEN Format(timestamp, 'hh') BETWEEN '18' AND '21' THEN 'Soirée'
        ELSE 'Autre'
    END
ORDER BY frappes DESC;

-- Fichier: info_sql/touches_speciales.sql
-- Analyse des touches spéciales (raccourcis, navigation, etc.)
SELECT 
    key_name,
    COUNT(*) as occurrences,
    ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM KeyPresses WHERE session_id = ?)), 2) as pourcentage
FROM KeyPresses 
WHERE session_id = ?
    AND key_name IN ('ctrl', 'alt', 'shift', 'tab', 'enter', 'backspace', 'delete', 'escape', 'up', 'down', 'left', 'right', 'home', 'end', 'page up', 'page down')
GROUP BY key_name
ORDER BY occurrences DESC;

-- Fichier: info_sql/rythme_frappe.sql
-- Analyse du rythme de frappe (pics d'activité)
SELECT 
    Format(timestamp, 'yyyy-mm-dd hh:nn') as minute,
    COUNT(*) as frappes_par_minute,
    CASE 
        WHEN COUNT(*) > 100 THEN 'Très élevé'
        WHEN COUNT(*) > 50 THEN 'Élevé'
        WHEN COUNT(*) > 20 THEN 'Modéré'
        WHEN COUNT(*) > 5 THEN 'Faible'
        ELSE 'Très faible'
    END as niveau_activite
FROM KeyPresses
WHERE session_id = ?
GROUP BY Format(timestamp, 'yyyy-mm-dd hh:nn')
HAVING COUNT(*) > 10  -- Filtrer les minutes avec peu d'activité
ORDER BY frappes_par_minute DESC;

-- Fichier: info_sql/erreurs_frappe.sql
-- Estimation des erreurs de frappe (backspace/delete après caractères)
WITH erreurs_potentielles AS (
    SELECT 
        timestamp,
        key_name,
        LAG(key_name) OVER (ORDER BY timestamp) as touche_precedente,
        LAG(timestamp) OVER (ORDER BY timestamp) as timestamp_precedent
    FROM KeyPresses 
    WHERE session_id = ?
)
SELECT 
    COUNT(*) as nb_corrections_potentielles,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM KeyPresses WHERE session_id = ?), 2) as taux_correction_pct
FROM erreurs_potentielles 
WHERE key_name IN ('backspace', 'delete')
    AND touche_precedente NOT IN ('backspace', 'delete', 'ctrl', 'alt', 'shift')
    AND DATEDIFF('s', timestamp_precedent, timestamp) < 5;  -- Correction dans les 5 secondes

-- Fichier: info_sql/sessions_comparaison.sql
-- Comparaison entre plusieurs sessions
SELECT 
    session_id,
    COUNT(*) as total_frappes,
    COUNT(DISTINCT key_name) as touches_uniques,
    MIN(timestamp) as debut_session,
    MAX(timestamp) as fin_session,
    ROUND((MAX(timestamp) - MIN(timestamp)) * 24 * 60, 2) as duree_minutes,
    ROUND(COUNT(*) / ((MAX(timestamp) - MIN(timestamp)) * 24 * 60), 2) as frappes_par_minute,
    ROUND(COUNT(*) / 5 / ((MAX(timestamp) - MIN(timestamp)) * 24 * 60), 2) as mots_par_minute_estime
FROM KeyPresses
GROUP BY session_id
ORDER BY debut_session DESC;

-- Fichier: info_sql/export_donnees.sql
-- Export complet pour analyse externe
SELECT 
    session_id,
    key_name,
    key_code,
    timestamp,
    Format(timestamp, 'yyyy-mm-dd') as date_seule,
    Format(timestamp, 'hh:nn:ss') as heure_seule,
    Format(timestamp, 'dddd') as jour_semaine,
    Format(timestamp, 'hh') as heure_24h
FROM KeyPresses
WHERE timestamp >= ? AND timestamp <= ?
ORDER BY timestamp;