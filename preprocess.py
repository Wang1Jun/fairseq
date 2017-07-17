import argparse
import os
from tokenizer import Tokenizer
import indexed_dataset
import dictionary

parser = argparse.ArgumentParser(description='Data pre-processing: Create dictionary and store data in binary format')
parser.add_argument('-s', '--source-lang', default=None, metavar='SRC',
                    help='source language')
parser.add_argument('-t', '--target-lang', default=None, metavar='TARGET',
                    help='target language')
parser.add_argument('--trainpref', metavar='FP', default="train", help='target language')
parser.add_argument('--validpref', metavar='FP', default="valid", help='valid language')
parser.add_argument('--testpref', metavar='FP', default="test", help='test language')
parser.add_argument('--destdir', metavar='DIR', default="data-bin", help='destination dir')
parser.add_argument('--ncandidates', metavar='N', default=1000, help='number of candidates per a source word')
parser.add_argument('--thresholdtgt', metavar='N', default=0, type=int, help='map words appearing less than threshold times to unknown')
parser.add_argument('--thresholdsrc', metavar='N', default=0, type=int, help='map words appearing less than threshold times to unknown')
parser.add_argument('--nwordstgt', metavar='N', default=-1, type=int, help='number of target words to retain')
parser.add_argument('--nwordssrc', metavar='N', default=-1, type=int, help='number of source words to retain')


def main():
    global args
    args = parser.parse_args()
    print(args)

    os.makedirs(args.destdir, exist_ok=True)

    src_dict = Tokenizer.build_dictionary(
        filename ="{}.{}".format(args.trainpref, args.source_lang))
    src_dict.save(os.path.join(args.destdir, "dict.{}.txt".format(args.source_lang)),
                  threshold = args.thresholdsrc)
    tgt_dict = Tokenizer.build_dictionary(
        filename ="{}.{}".format(args.trainpref, args.target_lang))
    tgt_dict.save(os.path.join(args.destdir, "dict.{}.txt".format(args.target_lang)),
                  threshold = args.thresholdtgt)

    def make_dataset(input_prefix, output_prefix, lang):
        dict = dictionary.Dictionary.load(os.path.join(args.destdir, "dict.{}.txt".format(lang)))
        ds = indexed_dataset.IndexedDatasetBuilder("{}/{}.{}-{}.{}.bin".format(
            args.destdir, output_prefix, args.source_lang,
            args.target_lang, lang))

        def consumer(tensor):
            ds.add_item(tensor)

        Tokenizer.binarize("{}.{}".format(input_prefix, lang), dict, consumer)
        ds.finalize("{}/{}.{}-{}.{}.idx".format(
            args.destdir, output_prefix,
            args.source_lang, args.target_lang, lang))


    make_dataset(args.trainpref, "train", args.source_lang)
    make_dataset(args.trainpref, "train", args.target_lang)
    make_dataset(args.validpref, "valid", args.source_lang)
    make_dataset(args.validpref, "valid", args.target_lang)
    make_dataset(args.testpref, "test", args.source_lang)
    make_dataset(args.testpref, "test", args.target_lang)


if __name__ == '__main__':
    main()
