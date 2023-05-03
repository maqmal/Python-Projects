from transformer_xl import Transformer_XL
import os
from glob import glob
import time
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

def main():
    # declare model
    model = Transformer_XL(
        checkpoint='train-checkpoint-chord',
        is_training=True)
    # prepare data
    midi_paths = glob('../dataset/*.midi') # you need to revise it
    training_data = model.prepare_data(midi_paths=midi_paths)
    
    output_checkpoint_folder = 'train-output-chord' # your decision
    if not os.path.exists(output_checkpoint_folder):
        os.mkdir(output_checkpoint_folder)
    
    print("====================================================================")
    print("Training start at : ",time.strftime("%H:%M:%S"))
    start_time = time.time()
    # finetune
    model.finetune(
        training_data=training_data,
        output_checkpoint_folder=output_checkpoint_folder)
    print("=================================================")
    print("training completed at: ", time.strftime("%H:%M:%S"))
    elapsed_time = time.time() - start_time
    print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    print("Training start at : ", start_time)
    print("=================================================")

    # close
    model.close()

if __name__ == '__main__':
    main()