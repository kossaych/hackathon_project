INSERT INTO message_insights
(message_id, mood, emotion, emotion_intensity, attention_signal, distraction, topic, created_at)
VALUES
-- Day 1
(1, 'positive', 'joy',        0.85, 'high',   0, 'focus',       '2025-03-01 10:15:00'),
(2, 'neutral',  'calm',       0.45, 'medium', 0, 'work',        '2025-03-01 11:40:00'),
(3, 'negative', 'stress',     0.70, 'low',    1, 'motivation',  '2025-03-01 18:20:00'),

-- Day 2
(4, 'positive', 'joy',        0.90, 'high',   0, 'focus',       '2025-03-02 09:30:00'),
(5, 'positive', 'calm',       0.60, 'medium', 0, 'work',        '2025-03-02 14:10:00'),
(6, 'negative', 'frustration',0.80, 'low',    1, 'motivation',  '2025-03-02 21:05:00'),

-- Day 3
(7, 'neutral',  'calm',       0.50, 'medium', 0, 'focus',       '2025-03-03 10:00:00'),
(8, 'negative', 'stress',     0.75, 'low',    1, 'work',        '2025-03-03 13:45:00'),
(9, 'positive', 'joy',        0.88, 'high',   0, 'motivation',  '2025-03-03 19:30:00'),

-- Day 4
(10,'neutral',  'calm',       0.40, 'medium', 0, 'focus',       '2025-03-04 09:50:00'),
(11,'negative', 'stress',     0.65, 'low',    1, 'work',        '2025-03-04 16:15:00'),

-- Day 5
(12,'positive', 'joy',        0.92, 'high',   0, 'focus',       '2025-03-05 08:40:00'),
(13,'positive', 'calm',       0.58, 'medium', 0, 'work',        '2025-03-05 12:20:00'),
(14,'negative', 'frustration',0.82, 'low',    1, 'motivation',  '2025-03-05 20:10:00');
