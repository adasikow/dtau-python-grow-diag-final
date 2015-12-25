from itertools import izip
import re
from sys import argv


def init_matrix(rows, columns, value):
    result = [[value for _ in range(columns)] for _ in range(rows)]
    return result


def intersect(e2f, f2e):
    rows = len(e2f)
    columns = len(f2e)
    result = init_matrix(rows, columns, False)
    for e in range(rows):
        for f in range(columns):
            result[e][f] = e2f[e][f] and f2e[f][e]

    return result


def union(e2f, f2e):
    rows = len(e2f)
    columns = len(f2e)
    result = init_matrix(rows, columns, False)
    for e in range(rows):
        for f in range(columns):
            result[e][f] = e2f[e][f] or f2e[f][e]

    return result


def neighboring_points((e_index, f_index), e_len, f_len):
    result = []

    if e_index > 0:
        result.append((e_index - 1, f_index))
    if f_index > 0:
        result.append((e_index, f_index - 1))
    if e_index < e_len - 1:
        result.append((e_index + 1, f_index))
    if f_index < f_len - 1:
        result.append((e_index, f_index + 1))
    if e_index > 0 and f_index > 0:
        result.append((e_index - 1, f_index - 1))
    if e_index > 0 and f_index < f_len - 1:
        result.append((e_index - 1, f_index + 1))
    if e_index < e_len - 1 and f_index > 0:
        result.append((e_index + 1, f_index - 1))
    if e_index < e_len - 1 and f_index < f_len - 1:
        result.append((e_index + 1, f_index + 1))

    return result


def aligned_e(e, f_len, alignment):
    for f in range(f_len):
        if alignment[e][f]:
            return True

    return False


def aligned_f(f, e_len, alignment):
    for e in range(e_len):
        if alignment[e][f]:
            return True

    return False


def grow_diag(union, alignment, e_len, f_len):
    new_points_added = True
    while new_points_added:
        new_points_added = False
        for e in range(e_len):
            for f in range(f_len):
                if alignment[e][f]:
                    for (e_new, f_new) in neighboring_points((e, f), e_len, f_len):
                        if not (aligned_e(e_new, f_len, alignment) and aligned_f(f_new, e_len, alignment))\
                                and union[e_new][f_new]:
                            alignment[e_new][f_new] = True
                            new_points_added = True


def final(alignment, e2f, f2e, e_len, f_len):
    for e in range(e_len):
        for f in range(f_len):
            if not (aligned_e(e, f_len, alignment) and aligned_f(f, e_len, alignment))\
                    and (e2f[e][f] or f2e[f][e]):
                alignment[e][f] = True


def grow_diag_final(e2f, f2e, e_len, f_len):
    alignment = intersect(e2f, f2e)
    grow_diag(union(e2f, f2e), alignment, e_len, f_len)
    final(alignment, e2f, f2e, e_len, f_len)
    return alignment


def parse_alignments(alignments_line, values):
    word_alignments_regex = ur"(\S+)\s\(\{([\s\d]*)\}\)"
    alignments = re.findall(word_alignments_regex, alignments_line)

    # Initialize array with False values for each pair of words
    rows = len(alignments)
    columns = len(values)
    result = init_matrix(rows, columns, False)

    # Align words
    for i in range(len(alignments)):
        alignment_values = alignments[i][1].split()
        for alignment in alignment_values:
            result[i][int(alignment)] = True

    return result


def print_alignments(alignments, e_len, f_len):
    result = ''
    for f in range(1, f_len):
        for e in range(1, e_len):
            if alignments[e][f]:
                result += str(f) + '-' + str(e) + ' '

    print result


def main():
    script, e2f_filename, f2e_filename = argv

    # States:
    # 0 - skip line with information about sentences length and alignment score
    # 1 - read sentence
    # 2 - read alignments and run GROW-DIAG-FINAL
    state = 0

    e_sentence = []
    f_sentence = []

    with open(e2f_filename) as e2f_file, open(f2e_filename) as f2e_file:
        for e2f_line, f2e_line in izip(e2f_file, f2e_file):
            if state == 0:
                state = 1
            elif state == 1:
                f_sentence = ['NULL'] + e2f_line.split()
                e_sentence = ['NULL'] + f2e_line.split()
                state = 2
            elif state == 2:
                alignments = grow_diag_final(
                        parse_alignments(e2f_line, f_sentence),
                        parse_alignments(f2e_line, e_sentence),
                        len(e_sentence), len(f_sentence))
                print_alignments(alignments, len(e_sentence), len(f_sentence))
                state = 0


if __name__ == '__main__':
    main()
