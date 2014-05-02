__author__ = 'toa'

import unittest
from twitterTokenizer import tokenizeRawTweetText


class TwitterTokenizerTestCase(unittest.TestCase):
    def test_tokenizeCreatesListOfToken(self):
        actual = tokenizeRawTweetText('This is a Tweet')
        self.assertIsInstance(actual, list)

    def test_commonEmoticonsAreSeparated(self):
        #TODO Add more
        actual = tokenizeRawTweetText('w00t =) :( :) :D :P >.> >.< :\'D')
        expected = ['w00t', '=)', ':(', ':)' ':D', ':P', '>.>', '>.<', ':\'D']
        self.assertEqual(actual, expected)

    def test_linksAreSeparated(self):
        actual = tokenizeRawTweetText('Go to https://www.this-is.net')
        expected = ['Go', 'to', 'https://www.this-is.net']
        self.assertEqual(actual, expected)

    def test_dollarAndPercentageAreNotSeparated(self):
        actual = tokenizeRawTweetText('I have 67$ 22%')
        expected = ['I', 'have', '67$', '22%']
        self.assertEqual(actual, expected)

    def test_timeIsSeparated(self):
        actual = tokenizeRawTweetText('It is 12:05 pm')
        expected = ['It', 'is', '12:05', 'pm']
        self.assertEqual(actual, expected)

    def test_dateFormatIsSeparated(self):
        actual = tokenizeRawTweetText('It is 12.04.2013')
        expected = ['It', 'is', '12.04.2013']
        self.assertEqual(actual, expected)

    def test_emailAdresseAreSeparated(self):
        actual = tokenizeRawTweetText('My email is myname@stud.tu-darmstadt.de')
        expected = ['My', 'email', 'is', 'myname@stud.tu-darmstadt.de']
        self.assertEqual(actual, expected)

    def test_numberWithCommaAreNotSeparated(self):
        actual = tokenizeRawTweetText('wir brauchen 12,5°C')
        expected = ['wir', 'brauchen', '12,5', '°C']
        self.assertEqual(actual, expected)

    def test_dottedNumbersWithUnitAreSeparated(self):
        actual = tokenizeRawTweetText('wir brauchen 12.5°C')
        expected = ['wir', 'brauchen', '12.5', '°C']
        self.assertEqual(actual, expected)

    def test_dottedNumbersAreNotSeparated(self):
        actual = tokenizeRawTweetText('wir brauchen 12.5')
        expected = ['wir', 'brauchen', '12.5']
        self.assertEqual(actual, expected)

    def test_wordsWithHyphenAreNotSeparated(self):
        actual = tokenizeRawTweetText('cdu-csu spd-fdp-grüne kein')
        expected = ['cdu-csu', 'spd-fdp-grüne', 'kein']
        self.assertEqual(actual, expected)

    def test_dashesAreSeparated(self):
        actual = tokenizeRawTweetText('-CSU wuff- ')
        expected = ['-', 'CSU', 'wuff', '-']
        self.assertEqual(actual, expected)

    def test_emptySpaceEndsHashtag(self):
        actual = tokenizeRawTweetText('Test #Hashtag zwei')
        expected = ['Test', '#Hashtag', 'zwei']
        self.assertEqual(actual, expected)

    def test_specialSignEndsHashtag(self):
        actual = tokenizeRawTweetText('My 6#miau #body+ #SPD-cdu #spd- #spd++#spd #cdu-#cdu #fpd/#markt')
        expected = ['My', '6', '#miau', '#body', '+', '#SPD', '-', 'cdu', '#spd', '-', '#spd', '++', '#spd', '#cdu', '-', '#cdu', '#fdp', '/', '#markt']
        print(actual)
        self.assertEqual(actual, expected)

    def test_hashtagWithMutedVowel(self):
        actual = tokenizeRawTweetText('My body #grüne' '@grün', 'grüne.', 'grüne-bla', 'grün\'s')
        expected = ['My', 'body', '#grüne', '@grün', 'grüne', '.', 'grüne-bla']
        print(actual)
        self.assertEqual(actual, expected)

    #def test_hashtagShouldStartWithAnCharacter(self):
    #    actual = tokenizeRawTweetText('My body #12spd')
    #    expected = ['My', 'body', '#', '12spd']
    #    print(actual)
    #    self.assertEqual(actual, expected)

    def test_tokenizeSeparatesRepeatedHashtags(self):
        actual = tokenizeRawTweetText('This is #Hash1#Hash2#Hash3')
        expected = ['This', 'is', '#Hash1', '#Hash2', '#Hash3']
        self.assertEqual(actual, expected)

    def test_edgePunctuationIsSeparated(self):
        actual = tokenizeRawTweetText('Wow!')
        expected = ['Wow', '!']
        self.assertEqual(actual, expected)

    def test_repeatedEdgePunctuationIsSeparated(self):
        actual = tokenizeRawTweetText('w00t!?!?!?!')
        expected = ['w00t', '!?!?!?!']
        self.assertEqual(actual, expected)

    def test_ApostrophesAreSeparated(self):
        actual = tokenizeRawTweetText('Susi\'s Hund Susi\"s Hund')
        #TODO Remove " also
        expected = ['Susi', 's', 'Hund', 'Susi', '\"s', 'Hund']
        self.assertEqual(actual, expected)

    def test_quotesAreSeparated(self):
        actual = tokenizeRawTweetText('\"Hund\" und \'Katze\'')
        expected = ['"', 'Hund', '"', 'und', '\'', 'Katze', '\'']
        self.assertEqual(actual, expected)

    def test_bracesAreSeparated(self):
        actual = tokenizeRawTweetText('(MyTeacher) {Some}')
        expected = ['(', 'MyTeacher', ')', '{', 'Some', '}']
        self.assertEqual(actual, expected)

    #TODO standard abbrev.


if __name__ == '__main__':
    unittest.main()
