import argparse
from typing import List, Set, Union
from collections import defaultdict
from utils import timed


class WordTrieNode:
    def __init__(self, value: str, parent: Union['WordTrieNode', None]):
        self.value = value
        self.parent = parent
        self.children = {}
        self.valid = False

    def get_word(self) -> str:
        if self.parent is not None:
            return self.parent.get_word() + self.value
        else:
            return self.value


class LetterBoxed:
    @timed
    def __init__(self, input_string: str, dictionary: str, len_threshold=3):
        # parse the input string (abc-def-ghi-jkl) into set of 4 sides
        self.input_string = input_string.lower()
        self.sides = {side for side in input_string.split('-')}
        self.puzzle_letters = {letter for side in self.sides for letter in side}
        self.len_threshold = len_threshold

        # build trie from .txt word list
        self.root = WordTrieNode('', None)
        with open(dictionary) as f:
            for line in f.readlines():
                self.add_word(line.strip().lower())

        # find all valid words in puzzle
        self.puzzle_words = self.get_puzzle_words()

        # map valid words by starting letter
        self.starting_letter_map = defaultdict(list)
        for word in self.puzzle_words:
            self.starting_letter_map[word[0]].append(word)

    def add_word(self, word) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = WordTrieNode(char, node)
            node = node.children[char]
        node.valid = True

    def _puzzle_words_inner(self, node: WordTrieNode, last_side: str) -> List[WordTrieNode]:
        valid_nodes = [node] if node.valid else []
        if node.children:
            for next_side in self.sides - {last_side}:
                for next_letter in next_side:
                    if next_letter in node.children:
                        next_node = node.children[next_letter]
                        valid_nodes += self._puzzle_words_inner(next_node, next_side)
        return valid_nodes

    @timed
    def get_puzzle_words(self) -> List[str]:
        all_valid_nodes = []
        for starting_side in self.sides:
            for starting_letter in starting_side:
                if starting_letter in self.root.children:
                    all_valid_nodes += self._puzzle_words_inner(self.root.children[starting_letter], starting_side)
        # only bother to build strings for usable nodes
        return [node.get_word() for node in all_valid_nodes]

    def _find_solutions_inner(self, partial_solution: List[str], used_letters: Set[str]) -> List[List[str]]:
        # termination criteria
        if len(used_letters) == 12:
            return [partial_solution]
        elif len(partial_solution) == self.len_threshold:
            return []

        # last letter of the last word
        next_letter = partial_solution[-1][-1]
        solutions = []
        for next_word in self.starting_letter_map[next_letter]:
            added_letters = set(next_word) - used_letters
            if added_letters:
                solutions += self._find_solutions_inner(partial_solution + [next_word], used_letters | added_letters)
        return solutions

    @timed
    def find_all_solutions(self) -> List[List[str]]:
        all_solutions = []
        for word in self.puzzle_words:
            all_solutions += self._find_solutions_inner([word], set(word))
        return all_solutions


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--puzzle', default='mrf-sna-opu-gci', type=str)
    parser.add_argument('--dict', default='words.txt', type=str)
    args = parser.parse_args()
    print("solving puzzle", args.puzzle)
    puzzle = LetterBoxed(args.puzzle, args.dict, len_threshold=2)
    print(len(puzzle.find_all_solutions()))

