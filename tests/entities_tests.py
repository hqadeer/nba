from nba_scrape import NBA
from nba_scrape import nba_exceptions
import unittest

class TestEntities(unittest.TestCase):

    def test_get_stat(self):
        '''Test the get_stat method of entities.py

        Specifically tests multiple instances, case insensitivity, None returns
        for valid stats and invalid queries, and TS% queries, and
        InvalidStatError raises for invalid stat queries.

        Also tests players that were traded mid-season, players that have no
        playoffs stats, null players, and players that have null values for
        many stats because they played before those were recorded.
        '''

        league = NBA()
        magic = league.get_player('mAGIC johnson')

        # Standard stat tests for a retired player.
        self.assertEqual(magic.get_stat('asT', '1988-89'), 12.8)
        self.assertEqual(magic.get_stat('tOv', '1984-85'), 4.0)
        self.assertEqual(magic.get_stat('OREB', '1990-91', playoffs=True), 1.2)
        self.assertEqual(magic.get_stat('GS', 'career', playoffs=True), 186)
        self.assertEqual(magic.get_stat('team', '1985-86'), "LAL")
        self.assertEqual(magic.get_stat('pts', '2005-06'), None)
        with self.assertRaises(nba_exceptions.InvalidStatError):
            magic.get_stat('unicorn', '1999-00')

        mario = league.get_player('mario chALmers')

        # Standard stat tests for an active player.
        self.assertEqual(mario.get_stat('team', '2015-16'), 'TOT')
        self.assertEqual(mario.get_stat('FT%', 'career', playoffs=True), 74.2)
        self.assertEqual(mario.get_stat('GP', '2017-18'), 66)
        self.assertEqual(mario.get_stat('3p%', '2010-11', playoffs=True), 38.1)
        self.assertEqual(mario.get_stat('fG%', '2017-18', playoffs=True), None)
        self.assertEqual(mario.get_stat('ft%', '2015-16'), 83.2)

        boogie = league.get_player('Demarcus Cousins')

        # Checking playoff stats of a player who's never been to the playoffs.
        self.assertEqual(boogie.get_stat('pts', 'career', playoffs=True), None)
        self.assertEqual(boogie.get_stat('pf', '2016-17', playoffs=True), None)
        with self.assertRaises(nba_exceptions.InvalidStatError):
            boogie.get_stat('unicorn', '2017-18', playoffs=True)

        booker = league.get_player('deVIN booker')

        # Same as above
        self.assertEqual(booker.get_stat('Blk', '2017-18'), 0.3)
        self.assertEqual(booker.get_stat('ast', 'career', playoffs=True), None)
        self.assertEqual(booker.get_stat('dreb', '2002-2342'), None)
        with self.assertRaises(nba_exceptions.InvalidStatError):
            booker.get_stat('unicorn', '2018-19', playoffs=True)

        kaj = league.get_player_by_id(76003)

        # Checking untracked stats of a retired player.
        self.assertEqual(kaj.get_stat('aGe', '1987-88'), 41)
        self.assertEqual(kaj.get_stat('age', 'career'), None)
        self.assertEqual(kaj.get_stat('3PM', '1985-86'), 0)
        self.assertEqual(kaj.get_stat('3pm', '1975-76'), None)
        self.assertEqual(kaj.get_stat('blk', '1972-73'), None)
        self.assertEqual(kaj.get_stat('tov', '1976-77'), None)

        # Checking stats of a player with no stats.
        no_stats = league.get_player('jaylen adams')
        self.assertEqual(no_stats.get_stat('pts', '1985-86'), None)
        self.assertEqual(no_stats.get_stat('ast', '1999-00', playoffs=True),
            None)
        with self.assertRaises(nba_exceptions.InvalidStatError):
            no_stats.get_stat('blobby', '2005-06')

        # Checking TS% queries.
        lebron = league.get_player('lebron james')
        self.assertTrue(abs(lebron.get_stat('ts%', '2017-18') - .621) < .01)
        self.assertTrue(abs(lebron.get_stat('ts%', '2013-14') - .649) < .01)
        self.assertTrue(abs(lebron.get_stat('ts%', '2015-16', playoffs=True)
                        - .585) < .2)

    def test_get_stats(self):
        '''Test the get_stats method of entities.py

        Tests all three modes, different season ranges, and various edge cases
        with invalid seasons, None stat values, and invalid stats.
        '''

        league = NBA()

        # Test season mode (default)
        butler = league.get_player('jimmy butler')
        season_stats = {'2012-13': ('CHI', 1.4, 0.8), '2013-14':
                        ('CHI', 2.6, 1.5), '2014-15': ('CHI', 3.3, 1.4)}
        self.assertEqual(butler.get_stats(['TEAM', 'AST', 'TOV'], '2012-15'),
                         season_stats)

        # Test playoffs mode
        playoff_stats = {'2012-13': (23, 12, 12), '2013-14': (24, 5, 5),
                         '2014-15': (25, 12, 12)}
        self.assertEqual(butler.get_stats(['age', 'gp', 'gs'], '2012-15',
                         mode='playoffs'), playoff_stats)

        # Test season and playoff stats together

        both_stats = {'2012-13': (23, 82, 20), '2013-14': (24, 67, 67),
                      '2014-15': (25, 65, 65), '2012-13P': (23, 12, 12),
                      '2013-14P': (24, 5, 5), '2014-15P': (25, 12, 12)}
        self.assertEqual(butler.get_stats(['age', 'gp', 'gs'], '2012-15',
                         mode='both'), both_stats)

        # Test with seasons parameter as 'career'
        career_stats = {'CAREER': (0.5, 1.5, 1.4)}
        self.assertEqual(butler.get_stats(['blk', 'tov', 'pf'], 'cAREEr'),
                         career_stats)

        # Test with no seasons parameter

        all_points = {'2011-12': (2.6,), '2012-13': (8.6,), '2013-14': (13.1,),
                      '2014-15': (20.0,), '2015-16': (20.9,),
                      '2016-17': (23.9,), '2017-18': (22.2,), 'CAREER':
                      (16.4,), '2011-12P': (0.0,), '2012-13P': (13.3,),
                      '2013-14P': (13.6,), '2014-15P': (22.9,), '2016-17P':
                      (22.7,), '2017-18P': (15.8,), 'CAREERP': (16.7,)}

        self.assertEqual(butler.get_stats(['pts'], mode='both'),
                         all_points)

        # Test with some none values
        all_age = {'2011-12': (22,), '2012-13': (23,), '2013-14': (24,),
                      '2014-15': (25,), '2015-16': (26,),
                      '2016-17': (27,), '2017-18': (28,), 'CAREER':
                      (None,)}
        self.assertEqual(butler.get_stats(['age']), all_age)

        kareem = league.get_player('kareem abdul-jabbar')
        rebounds = {'1971-72': (None, None), '1972-73': (None, None),
                    '1973-74': (3.5, 11.0), '1974-75': (3.0, 11.0)}
        self.assertEqual(kareem.get_stats(['oreb', 'dreb'], '1971-75'),
                         rebounds)

        # Test with all invalid seasons
        self.assertEqual(butler.get_stats(['pts', 'reb'], '2000-05'), {})

        # Test with some invalid seasons
        ptsrebs = {'2011-12': (2.6, 1.3), '2012-13': (8.6, 4.0)}
        self.assertEqual(butler.get_stats(['pts', 'reb'], '2010-13'), ptsrebs)

        # Test with some invalid stats
        with self.assertRaises(nba_exceptions.InvalidStatError):
            butler.get_stats(['pts', 'OFFRTG'], '2015-18')

        # Test for TS% queries
        pts_ts = {'2015-16': (20.9, 5.3, 0.564, 4.8), '2016-17':
                  (23.9, 6.2, 0.585, 5.5), '2017-18':
                  (22.2, 5.3, 0.591, 4.9)}

        self.assertEqual(
            butler.get_stats(['pts', 'reb', 'ts%', 'ast'], '2015-18'), pts_ts
        )


    def test_get_year_range(self):
        '''Test the get_year_range method of the Player class in entities.py'''

        league = NBA()
        kobe = league.get_player('kobe bryant')

        years_a = ['2008-09', '2009-10', '2010-11']
        self.assertEqual(kobe.get_year_range('2008-11'), years_a)

        years_b = ['1995-96', '1996-97', '1997-98', '1998-99',
                   '1999-00', '2000-01']
        self.assertEqual(kobe.get_year_range('1995-01'), years_b)
        self.assertEqual(kobe.get_year_range(None), None)
        self.assertEqual(kobe.get_year_range('CArEEr'), ['CAREER'])


if __name__ == "__main__":

    unittest.main()
