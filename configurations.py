configurations = [
    {
        "robots": [
            {"position": (7, 1), "color": "Re"},
            {"position": (3, 5), "color": "Bl"},
            {"position": (6, 6), "color": "Gr"},
            {"position": (10, 8), "color": "Ye"}
        ],
        "walls": [
            (0, 0, 'L'),
            (1, 6, 'R'),
            (2, 2, 'T'),
            (2, 2, 'B'),
            (4, 5, 'R'),
            (6, 1 ,'T'),

        ],
        "targets": [
            {"position": (15, 1), "color": "Re"},
            {"position": (9, 7), "color": "Re"},
            {"position": (2, 3), "color": "Bl"}
        ],
    },
{
        "robots": [
            {"position": (5, 4), "color": "Re"},
            {"position": (10, 6), "color": "Bl"},
            {"position": (3, 8), "color": "Gr"},
            {"position": (12, 12), "color": "Ye"}
        ],
        "walls": [
            # Top-left quadrant
            (0, 3, 'R'), (0, 3, 'B'),
            (2, 6, 'L'), (2, 6, 'T'),
            # Top-right quadrant
            (4, 9, 'T'), (4, 9, 'R'),
            (6, 12, 'L'), (6, 12, 'B'),
            # Bottom-left quadrant
            (10, 2, 'T'), (10, 2, 'R'),
            (12, 5, 'B'), (12, 5, 'L'),
            # Bottom-right quadrant
            (14, 10, 'L'), (14, 10, 'B'),
            (15, 15, 'T'), (15, 15, 'R'),
        ],
        "targets": [
            {"position": (8, 4), "color": "Re"},  # Accessible depuis le robot rouge
            {"position": (6, 6), "color": "Bl"},  # Accessible depuis le robot bleu
            {"position": (3, 10), "color": "Gr"},  # Accessible depuis le robot vert
            {"position": (14, 12), "color": "Ye"},  # Accessible depuis le robot jaune
        ],
    },
    {
        "robots": [
            {"position": (5, 7), "color": "Re"},
            {"position": (7, 14), "color": "Bl"},
            {"position": (0, 5), "color": "Gr"},
            {"position": (15, 14), "color": "Ye"}
        ],
        "walls": [
            (0,5,'R'), (0,9,'R'),
            (1,13,'T'), (1,13,'R'),
            (2,3,'L'), (2,3,'T'),(2,9,'L'), (2,9,'T'),
            (3,5,'L'), (3,5,'B'),
            (4,0,'T'), (4,2,'T'),(4,2,'R'), (4,15,'B'),
            (5,4,'B'), (5,4,'R'),
            (6,10,'B'), (6,10,'R'), (6,14,'B'), (6,14,'L'),
            (9,15,'B'),
            (10,5,'B'), (10,5,'L'), (10,8,'R'), (10,8,'B'),
            (11,1,'T'),(11,1,'L'), (11,13,'T'),(11,13,'L'),
            (12,6,'T'),(12,6,'R'),
            (13,9,'B'),(13,9,'L'),
            (14,0,'T'),(14,3,'B'),(14,3,'R'),(14,14,'T'),(14,14,'R'),
            (15,5,'R'),(15,12,'L')
        ],
        "targets": [
            {"position": (1, 13), "color": "Bl"},  # Accessible avec rebonds sur 2 murs
            {"position": (3, 5), "color": "Bl"},  # Accessible avec rebonds sur 2 murs
            {"position": (13, 9), "color": "Gr"},  # Accessible avec rebonds sur 2 murs
            {"position": (11, 1), "color": "Bl"},  # Accessible avec rebonds sur 2 murs

        ],
    }
]