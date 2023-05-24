import copy
import numpy as np
from scipy import stats

class Website:
    def __init__(self, id, title, url):
        self.id = id
        self.title = title
        self.url = url
        self.visit_times = 0
        self.count = 0
        self.visitors = []
        self.children = {}
        self.parent = None
        self.next = None

    def inc(self, numOccur=1):
        """
        增加节点的出现次数
        :param numOccur:
        :return:
        """
        self.count += numOccur

    def disp(self, ind=1):
        """
        输出节点和子节点的FP树结构
        :param ind:
        :return:
        """
        print('  ' * ind, self.id, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)

    def create_child(self, child):
        if child not in self.children.values():
            self.children[child.id] = child


class User:
    def __init__(self, id, visits):
        self.id = id
        self.visits = visits


class FPTree:
    def __init__(self, website_map):
        self.root = Website("root", "root", None)
        self.head_list = {}
        self.website_map = website_map

    def add(self, seq, inc_num=1):
        current = self.root
        for item in seq:

            if item not in current.children.keys():
                next_node = copy.deepcopy(self.website_map[item])
                next_node.inc(inc_num)
                current.children[item] = next_node
                next_node.parent = current
            else:
                next_node = current.children[item]
                next_node.inc(inc_num)
            if item not in self.head_list.keys():
                self.head_list[item] = next_node
            else:
                cw = self.head_list[item]
                while cw != next_node:
                    if cw.next is not None:
                        cw = cw.next
                    else:
                        cw.next = next_node
                        break

            current = next_node

    def mining(self, level, threshold=10):
        if level > 100:
            print("递归层数超过100")
            print(self.head_list.keys())
        results = {}
        for key, value in self.head_list.items():
            results[key] = []
            sequences = []
            f = []
            while value is not None:
                next_value = value.next
                sequence = []
                if value.count >= threshold:
                    c = copy.copy(value.count)
                    while value.id != "root":
                        sequence.append(copy.copy(value.id))
                        value = value.parent
                    if len(sequence) == 1:
                        results[key].append([sequence, c])
                    else:
                        sequence = sequence[1:]
                        sequence.reverse()
                        sequences.append(sequence)
                        f.append(c)
                value = next_value
            fp_tree = FPTree(self.website_map)
            if len(sequences) > 1:
                for i, s in enumerate(sequences):
                    fp_tree.add(s, f[i])
                r = fp_tree.mining(level + 1)
                for v in r.values():
                    for vv in v:
                        vv[0].append(key)
                    results[key] += v
            elif len(sequences) == 1:
                ss = sequences[0]
                ss.append(key)
                results[key].append([ss, f[0]])
        return results


def post_process(results, k_itemset=5):
    output = {}
    for i in range(k_itemset):
        output[str(i + 1)] = []
    for key, value in results.items():
        for v in value:
            if 0 < len(v[0]) <= k_itemset:
                output[str(len(v[0]))].append(v)
    for key in output.keys():
        output[key] = sorted(output[key], key=lambda x: x[1], reverse=True)
    return output


def support_confidence_lift(user_num, website_map, item_set):
    support = []
    confidence = []
    lift_x2 = []
    for item in item_set:
        s = item[1] / user_num
        c1 = website_map[item[0][0]].visit_times / user_num
        c2 = website_map[item[0][1]].visit_times / user_num
        w1 = website_map[item[0][0]].url
        w2 = website_map[item[0][1]].url
        m = np.array([[item[1],website_map[item[0][1]].visit_times-item[1]],
                      [website_map[item[0][0]].visit_times-item[1],user_num-website_map[item[0][1]].visit_times-website_map[item[0][0]].visit_times+item[1]]])
        r = stats.chi2_contingency(m, correction=False)
        support.append([w1, w2, s])
        confidence.append([w1, w2, s / c1, s / c2])
        lift_x2.append([w1, w2, s / c1 / c2, r[0], r[1]])  # web1,web2,lift,x2,p
    confidence = sorted(confidence, key=lambda x: x[2], reverse=True)
    lift = sorted(lift_x2, key=lambda x: x[2], reverse=True)

    return support, confidence, lift


def test_value(user_map):
    # [['1008', '1004', '1018', '1017'], 252],
    c = 0
    for user in user_map.values():
        l = user.visits
        if '1008' in l and '1004' in l and '1018' in l and '1017' in l:
            if len(l) >= 4 and (l.index('1008') < l.index('1004')) and (l.index('1004') < l.index('1018')) and (
                    l.index('1018') < l.index('1017')):
                c += 1
    return c
