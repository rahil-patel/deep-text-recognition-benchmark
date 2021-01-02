from os.path import splitext, basename, sep, join


def main():
    lines = [line.strip().split() for line in open('log.txt') if 'query' in line if len(line.split()) == 3]

    data = {}
    for path, text, conf in lines:
        if float(conf) < 0.5:# or '..' in text or '$.' in text:
            continue

        name, cc = splitext(basename(path))[0].split('--')
        data.setdefault(name, []).append((cc.replace('-', ' '), text))

    data_dir = lines[0][0].rsplit(sep, 3)[0]
    for name, preds in data.items():
        gt_path = join(data_dir, f'{name}_gt.txt')
        lines = [line.strip() for line in open(gt_path)]

        for cc, text in preds:
            for i, line in enumerate(lines):
                if cc in line and '0' * 12 in line:
                    lines[i] = ' '.join(line.split(' ')[:4] + [text.upper()])

        with open(gt_path, 'w') as f:
            for line in lines:
                f.write(f'{line}\n')


if __name__ == '__main__':
    main()
