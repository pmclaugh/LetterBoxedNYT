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

        # build trie from newline-delimited .txt word list
        self.root = WordTrieNode('', None)
        with open(dictionary) as f:
            for line in f.readlines():
                self.add_word(line.strip().lower())

        # find all valid words in puzzle
        self.puzzle_words = self.get_puzzle_words()

        # puzzle_graph[starting_letter][ending_letter] = {{letters}: [words]}
        # e.g. puzzle_graph['f']['s'] = {{'a','e','f','r','s'} : ['fares', 'fears', 'farers', 'fearers']}
        self.puzzle_graph = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for word in self.puzzle_words:
            self.puzzle_graph[word[0]][word[-1]][frozenset(word)].append(word)

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

    def _find_solutions_inner(self, path_words: List[List[str]], letters: Set[str], next_letter: str) -> List[List[List[str]]]:
        # termination criteria
        if len(letters) == 12:
            return [path_words]
        elif len(path_words) == self.len_threshold:
            return []

        solutions = []
        for last_letter in self.puzzle_graph[next_letter]:
            for letter_edge, edge_words in self.puzzle_graph[next_letter][last_letter].items():
                if letter_edge - letters:
                    solutions += self._find_solutions_inner(path_words + [edge_words], letters | letter_edge, last_letter)
        return solutions

    @timed
    def find_all_solutions(self) -> List[List[str]]:
        all_solutions = []
        for first_letter in self.puzzle_letters:
            for last_letter in self.puzzle_letters:
                for letter_edge, edge_words in self.puzzle_graph[first_letter][last_letter].items():
                    all_solutions += self._find_solutions_inner([edge_words], letter_edge, last_letter)
        return all_solutions


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--puzzle', default='mrf-sna-opu-gci', type=str, help='puzzle input in abd-def-ghi-jkl format')
    parser.add_argument('--dict', default='words.txt', type=str, help='path to newline-delimited text file of valid words')
    parser.add_argument('--len', default=3, type=int, help='maximum length, in words, of solutions')
    args = parser.parse_args()
    print("solving puzzle", args.puzzle)
    puzzle = LetterBoxed(args.puzzle, args.dict, len_threshold=args.len)
    solns = puzzle.find_all_solutions()
    full_count = 0
    for meta_solution in solns:
        count = 1
        for element in meta_solution:
            count *= len(element)
        full_count += count
    print(len(solns))
    print(full_count)


