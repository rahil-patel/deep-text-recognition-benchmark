from os.path import basename, splitext, sep, join

from nltk.metrics.distance import edit_distance


def main():
    lines = [line.strip().split() for line in open('log.txt') if 'dataset' in line]

    data = {}
    for path, text, conf in lines:
        #if float(conf) < 0.5:
        #    continue

        name, cc = splitext(basename(path))[0].split('--')
        data.setdefault(name, []).append((cc.replace('-', ' '), text, conf))

    data_dir = lines[0][0].rsplit(sep, 3)[0]
    for name, preds in data.items():
        gt_path = join(data_dir, f'{name}_gt.txt')
        lines = [line.strip() for line in open(gt_path)]

        for cc, text, conf in preds:
            for i, line in enumerate(lines):
                if cc in line:
                    gt_text = line.split()[-1].lower()

                    if len(gt_text) > len(text):
                        dist = 1 - edit_distance(text, gt_text) / len(gt_text)
                    else:
                        dist = 1 - edit_distance(text, gt_text) / len(text)

                    print('{}\t{}\t{}\t{}\t{}\t{}'.format(name, cc, text, conf, gt_text, dist))


if __name__ == '__main__':
    main()
