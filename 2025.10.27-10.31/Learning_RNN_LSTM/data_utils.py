"""
Check Data midi files is or not have music
"""
import torch
import numpy as np
import os
from music21 import converter, stream, instrument, stream, note, tempo, midi
from grammar import unparse_grammar
from qa import prune_grammar, prune_notes, clean_up_notes

def check_data(data_file):
    midi_data = converter.parse(data_file)

    print("\n--- 自动化轨道检查 ---")

    # midi_data.parts 是访问所有轨道的标准方式
    print(f"文件总共有 {len(midi_data.parts)} 个轨道 (Parts)。")

    # 遍历所有轨道
    for i, part in enumerate(midi_data.parts):
        print(f"\n--- 轨道 {i} ('midi_data[{i}]') ---")
        
        # 2.1 尝试获取这个轨道的乐器名称
        # .getInstrument() 是一个好用的函数
        inst = part.getInstrument()
        if inst:
            print(f"  乐器: {inst.instrumentName}")
        else:
            print("  乐器: 未指定")
            
        # 2.2 查看这个轨道里包含哪些类型的 '元素'
        # .classes 会告诉你这个轨道里有什么 (Note, Chord, Voice...)
        print(f"  包含的元素类型: {part.classes}")
        
        # 2.3 专门检查它是否包含 'Voice' (这正是你出错的地方)
        # 这等价于 deepjazz 脚本中的 .getElementsByClass(stream.Voice)
        voices = part.getElementsByClass(stream.Voice)
        
        print(f"  找到 'stream.Voice' 对象的数量: {len(voices)}, 轨道{i}")

def generate_music(model, 
                           indices_val, 
                           original_chords_stream, 
                           n_values, 
                           n_a, 
                           Ty_per_measure=50, 
                           temperature=0.0,
                           device='cuda'):
    """
    Parameters:
    model: trained Pytorch_models
    indices_val (dict): 索引 -> Token (来自 get_corpus_data)
    original_chords_stream (stream.Stream): 原始伴奏 (来自 get_musical_data)
    n_values (int): 词汇表大小 (例如 78)
    n_a (int): 隐藏层维度 (例如 64)
    Ty_per_measure (int): 为每个小节生成多少个 token
    temperature (float): 采样温度 (0.0 = argmax，复现原始逻辑)
    device (str): 'cuda' 或 'cpu'
    """
    
    print("开始生成音乐...")
    model.eval() # 确保模型处于评估模式
    
    # 1. 初始化空的输出流
    out_stream = stream.Stream()
    curr_offset = 0.0

    # 2. 将原始伴奏流按小节切分
    # 我们使用 .makeMeasures()，这比原版脚本中的 group 逻辑更健壮
    try:
        accompaniment_measures = original_chords_stream.makeMeasures()
        num_measures = len(accompaniment_measures)
        print(f"伴奏已切分为 {num_measures} 个小节。")
    except Exception as e:
        print(f"处理伴奏流时出错: {e}")
        print("请确保 'original_chords_stream' 是一个有效的 music21 Stream 对象。")
        return None
        
    if num_measures == 0:
        print("错误：伴奏流不包含任何小节。")
        return None

    # 3. 循环遍历每个小节，为其生成新的旋律
    for i in range(num_measures):
        curr_chords_measure = accompaniment_measures[i]

        # a. 为生成器准备初始输入 (batch_size=1)
        x_initializer = torch.zeros(1, n_values).to(device)
        a_initializer = torch.zeros(1, n_a).to(device)
        c_initializer = torch.zeros(1, n_a).to(device)

        # b. 生成一个 token 序列
        with torch.no_grad():
            generated_sequence_tensor = model.generate(
                x_initializer, 
                a_initializer, 
                c_initializer, 
                Ty=Ty_per_measure,
                temperature=temperature # 0.0 复现原始的 argmax
            )
        
        # c. 将 Tensor 转换为 token 索引列表
        generated_indices = generated_sequence_tensor.to('cpu').numpy().squeeze().tolist()
        # ----------------------------------------------------
        
        # d. 解码：将索引列表转换回语法字符串
        pred_tokens = [indices_val[idx] for idx in generated_indices]
        predicted_grammar_str = ' '.join(pred_tokens)
        
        # e. 后处理 (Post-processing)，同 data_utils.py
        predicted_grammar_str = predicted_grammar_str.replace(' A',' C').replace(' X',' C')
        predicted_grammar_str = prune_grammar(predicted_grammar_str)

        # f. 反解析 (Unparsing)：将语法字符串转换为 music21 音符
        # 我们使用当前小节的和弦 (curr_chords_measure) 作为上下文
        try:
            sounds = unparse_grammar(predicted_grammar_str, curr_chords_measure)
        except Exception as e:
            # print(f"警告：在小节 {i} 反解析语法时出错: {e}。跳过此小节。")
            sounds = [] # 创建一个空列表以跳过

        # g. 质量保证 (QA)
        sounds = prune_notes(sounds)
        sounds = clean_up_notes(sounds)

        if len(sounds)>0:
            print(f"小节 {i+1}/{num_measures}: 生成了 {len(sounds)} 个音符事件。")

        # h. 将新生成的旋律 (sounds) 和原始伴奏 (curr_chords_measure) 插入到输出流
        for m in sounds:
            out_stream.insert(curr_offset + m.offset, m)
        for mc in curr_chords_measure.notesAndRests: # 只插入音符和休止符
            out_stream.insert(curr_offset + mc.offset, mc)
            
        # i. 更新偏移量，准备下一个小节
        curr_offset += curr_chords_measure.duration.quarterLength

    # 4. 设置速度并保存 MIDI 文件
    out_stream.insert(0.0, tempo.MetronomeMark(number=130)) # 同原版
    
    # 确保 output 文件夹存在
    if not os.path.exists("output"):
        os.makedirs("output")
        
    file_path = "output/my_music.midi"
    mf = midi.translate.streamToMidiFile(out_stream)
    mf.open(file_path, 'wb')
    mf.write()
    mf.close()
    
    print(f"音乐生成完毕！已保存至: {file_path}")
    
    return out_stream