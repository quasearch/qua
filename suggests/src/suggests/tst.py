'''Ternary search tree implementstion'''
import re


class Node:

    def __init__(self, data=None, rating=None, payload=None):

        self.data = data
        self.also = []
        self.rating = rating
        self.payload = payload

        self.left = None
        self.right = None
        self.eq = None

    def __str__(self):

        return '<Node[{0}][{1}]'.format(self.data, self.rating)

    def __repr__(self):

        return self.__str__()


class TernarySearchTree:

    def __init__(self):

        self.root = Node()
        self._count_leaves = 0
        self._cache = {}

    def __str__(self):

        return '<TernarySearchTree: {0} words>'.format(self._count_leaves)

    def __repr__(self):

        return self.__str__()

    def __contains__(self, item):

        child = self.search(item)

        if child is not None:
            return child.rating is not None
        else:
            return False

    def __len__(self):

        return self._count_leaves

    def _insert(self, node, char, rating=None, payload=None, also=None):

        if node.data is None:
            node.data = char

            if rating is None:
                node.eq = Node()
                return node.eq

            # When rating is not None -> last char in inserting word
            else:
                # When inserting value which is already in tree nothing
                # happen
                if node.rating is None:
                    node.rating = rating
                    node.payload = payload
                    self._count_leaves += 1

                if also is not None and also not in node.also:
                    node.also.append(also)

                return None
        elif also is not None and rating is not None:
            if also not in node.also:
                node.also.append(also)

        if char == node.data:
            # middle
            if node.eq is None:
                node.eq = Node()
            return node.eq
        elif char > node.data:
            # right
            if node.right is None:
                node.right = Node()
            return self._insert(node.right, char, rating)
        else:
            # left
            if node.left is None:
                node.left = Node()
            return self._insert(node.left, char, rating)

    def _search(self, node, char, end=False):

        if node is None or node.data is None:
            return None

        if node.data == char:
            if not end:
                return node.eq
            else:
                return node
        elif char > node.data:
            return self._search(node.right, char, end)
        else:
            return self._search(node.left, char, end)

    def _traverse(self, node, prefix, buffer, full_traverse=True):

        if full_traverse:
            leaves = (node.left, node.eq, node.right)
        else:
            leaves = (None, node.eq, None)

        for i in range(3):
            if leaves[i] is not None:
                if i == 1:
                    self._traverse(leaves[i], prefix + node.data, buffer)
                else:
                    self._traverse(leaves[i], prefix, buffer)

        if node.rating is not None:
            if len(node.also) > 0:
                for als in node.also:
                    buffer.append((node.rating, als, node.payload))
            else:
                buffer.append((node.rating, prefix + node.data, node.payload))

    def _prefixes(self, string):

        res = []

        while string:
            res.append(string)
            string = string[:len(string) - 1]

        return res

    def _query_parts(self, query):

        parts = set(re.findall(r"(\w+)", query, re.UNICODE))
        parts.update(query.split(' '))

        excess = set()

        for elem in parts:
            if query.startswith(elem):
                excess.add(elem)

        return list(parts - excess)

    def optimize(self, common_num=10, cache_threshold=1000):

        prefixes = set([])

        for _, word in self.common_prefix(
                '', limit=self._count_leaves, with_payload=False):
            prefixes.update(self._prefixes(word))

        prefixes.add('')

        for prefix in prefixes:
            leaves = self.common_prefix(prefix, limit=self._count_leaves)

            if len(leaves) >= cache_threshold:
                self._cache[prefix] = sorted(
                    leaves, key=lambda it: it[0], reverse=True)[:common_num]

    def insert(self, string, rating, payload=None, also=None):

        node = self.root
        lstring = len(string)

        for i in range(lstring):
            # If this is the last letter -> pass rating
            if i == lstring - 1:
                self._insert(
                    node, string[i],
                    rating=rating,
                    payload=payload,
                    also=also)
            else:
                node = self._insert(
                    node, string[i],
                    payload=payload,
                    also=also)

        # Adding also values

        for word in self._query_parts(string):
            self.insert(word, rating // 2, payload, string)

    def search(self, string):

        node = self.root
        lstring = len(string)

        for i in range(lstring):
            if i == lstring - 1:
                node = self._search(node, string[i], True)
            else:
                node = self._search(node, string[i])

            if node is None:
                return None

        return node

    def common_prefix(self, prefix, limit=10, with_payload=True):

        if prefix in self._cache:
            return self._cache[prefix][:limit]

        if prefix == '':
            child = self.root
            full_traverse = True
        else:
            child = self.search(prefix)
            full_traverse = False

        # Nothing found
        if child is None:
            return []

        buffer = []
        self._traverse(child, prefix[0:-1], buffer, full_traverse)

        # Removing also duplicates
        uniq_buffer = []
        dup = set([])
        for item in buffer:
            if item[1] not in dup:
                # Recalc rate by substract len
                new_rate = item[0] - len(item[1])

                uniq_buffer.append((new_rate, item[1], item[2]))
                dup.add(item[1])

        buffer = uniq_buffer[:limit]

        buffer.sort(key=lambda it: it[0], reverse=True)

        if not with_payload:
            buffer = [(it[0], it[1]) for it in buffer]

        return buffer

    def get(self, item, with_payload=False):

        child = self.search(item)

        if child is not None:
            if with_payload:
                return child.rating, child.payload
            else:
                return child.rating
