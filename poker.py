#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J),
# дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts),
# 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertools.
# Можно свободно определять свои функции и т.п.
# -----------------
from itertools import groupby, combinations, product, chain


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return 8, max(ranks)
    if kind(4, ranks):
        # Need to save paired rank no ignore it next time
        trin = kind(4, ranks)
        return 7, trin, kind(1, ranks, [trin])
    if kind(3, ranks):
        # Need to save paired rank no ignore it next time
        trin = kind(3, ranks)
        return 6, trin, kind(2, ranks, [trin])
    if flush(hand):
        return 5, ranks
    if straight(ranks):
        return 4, max(ranks)
    if kind(3, ranks):
        return 3, kind(3, ranks), ranks
    if two_pair(ranks):
        return 2, two_pair(ranks), ranks
    if kind(2, ranks):
        return 1, kind(2, ranks), ranks
    return 0, ranks


# Ранги: 2, 3, 4, 5, 6, 7, 8, 9,
# 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
_sort_dict = {
    **{str(x): x for x in range(2, 10)},
    'T': 10,
    'J': 11,
    'Q': 12,
    'K': 13,
    'A': 14
}


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    return [_sort_dict[x[0]]
            for x in sorted(hand, key=lambda elem: _sort_dict[elem[0]])]


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    return all(x[1] == hand[0][1] for x in hand)


def straight(ranks):
    """
    Возвращает True, если отсортированные ранги
    формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)
    """
    return all(ranks[x] + 1 == ranks[x+1] for x in range(len(ranks)-1))


def kind(n, ranks, ignore_list=None):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    if ignore_list is None:
        ignore_list = []
    for key, group in groupby(ranks):
        if sum(1 for x in group) >= n and key not in ignore_list:
            return key
    return None


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    f_key = None
    s_key = None
    for key, group in groupby(ranks):
        if sum(1 for x in group) >= 2:
            if f_key is None:
                f_key = key
            else:
                s_key = key
    return (f_key, s_key) if s_key is not None else None


def best_hand_of_list(hands_list):
    """Search best hand from list"""
    result = None
    result_hand = None
    for hand, hand_result in [(x, hand_rank(x)) for x in hands_list]:
        if result is None or result[0] < hand_result[0]:
            result_hand, result = hand, hand_result
        elif result[0] == hand_result[0]:
            for tindex in range(len(result)):
                if hand_result[tindex] is None or result[tindex] > hand_result[tindex]:
                    break
                if result[tindex] < hand_result[tindex]:
                    result_hand, result = hand, hand_result
                    break
    return result_hand


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    return best_hand_of_list(combinations(hand, 5))


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    all_possible_hands = [hand]
    jokers = [
        ('?B', [x[0]+x[1] for x in product(_sort_dict.keys(), ['C', 'S'])]),
        ('?R', [x[0]+x[1] for x in product(_sort_dict.keys(), ['H', 'D'])])
    ]
    # change all jokers
    for joker in jokers:
        # if joker in first, then we have it in all
        if joker[0] in all_possible_hands[0]:
            # create all combinations (hand, joker_value) and replace joker
            all_possible_hands = [
                [y if y != joker[0] else x[1] for y in x[0]]
                for x in product(all_possible_hands, joker[1]) if x[1] not in x[0]
            ]
    # create all 5-combinations from all "joker"-combinations
    return best_hand_of_list(
        chain.from_iterable(combinations(x, 5) for x in all_possible_hands)
    )


def test_best_hand():
    print("test_best_hand...")
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


def test_best_wild_hand():
    print("test_best_wild_hand...")
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()
