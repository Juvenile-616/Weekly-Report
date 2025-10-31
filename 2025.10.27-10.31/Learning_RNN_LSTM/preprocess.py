'''
preprocess.py (健壮版)
作者: Alfajer (基于原版 deepjazz 脚本的意图重写)
目的: 以健壮且通用的方式解析 MIDI 文件，提取旋律和伴奏，
      并生成 "abstract grammars" (抽象语法)。
'''

import os
from music21 import converter, stream, chord, instrument, note
from collections import OrderedDict
import sys

# 确保 grammar.py 在路径中，并且可以被导入
try:
    from grammar import parse_melody
except ImportError:
    print("错误: 无法导入 'grammar.py'。", file=sys.stderr)
    print("请确保 grammar.py 与 preprocess.py 在同一目录中。", file=sys.stderr)
    sys.exit(1)

#----------------------------私有辅助函数----------------------------------#

def __get_abstract_grammars(melody_stream, chord_stream):
    """
    辅助函数：给定旋律流和和弦流，逐小节生成抽象语法。

    参数:
    melody_stream (stream.Stream): 包含旋律音符的 music21 Stream
    chord_stream (stream.Stream): 包含和弦分析的 music21 Stream (通常来自 .chordify())
    """
    
    print("正在将旋律和和弦按小节对齐...")
    
    # 1. 使用 music21 的标准方法按拍号创建小节
    # 这远比原版 `int(n.offset / 4)` 的方法健壮
    melody_measures_stream = melody_stream.makeMeasures()
    chord_measures_stream = chord_stream.makeMeasures()

    # 2. 获取小节列表
    melody_measures = melody_measures_stream.getElementsByClass(stream.Measure)
    chord_measures = chord_measures_stream.getElementsByClass(stream.Measure)

    num_measures = min(len(melody_measures), len(chord_measures))
    if len(melody_measures) != len(chord_measures):
        print(f"警告: 旋律小节数 ({len(melody_measures)}) 与 和弦小节数 ({len(chord_measures)}) 不匹配。")
        print(f"将只处理共同的前 {num_measures} 个小节。")

    abstract_grammars = []
    
    print(f"正在逐小节生成语法 (共 {num_measures} 个小节)...")
    
    # 3. 遍历所有对齐的小节
    for i in range(num_measures):
        m_measure = melody_measures[i]
        c_measure = chord_measures[i]
        
        # 4. 调用 grammar.py 中的解析器
        # `parse_melody` 期望两个 stream 对象 (Measure 是 Stream 的子类)
        try:
            parsed = parse_melody(m_measure, c_measure)
            if parsed: # 确保 `parse_melody` 返回了非空内容
                abstract_grammars.append(parsed)
        except Exception as e:
            print(f"在处理小节 {i} 时出错: {e}")
            # print(f"旋律: {m_measure.getElementsNotOfClass(note.Rest)}")
            # print(f"和弦: {c_measure.getElementsByClass(chord.Chord)}")
            pass # 跳过这个小节

    print("语法生成完毕。")
    return abstract_grammars

#----------------------------公共函数----------------------------------#

def get_musical_data(data_fn, 
                     melody_part_index=5, 
                     accompaniment_part_indices=[0, 1, 6, 7]):
    """
    从 MIDI 文件加载音乐数据，提取旋律和伴奏，并生成抽象语法。

    参数:
    data_fn (str): MIDI 文件的路径
    melody_part_index (int): 旋律所在的轨道索引 (Part index)。
                             (原版 deepjazz 使用 5)
    accompaniment_part_indices (list[int]): 伴奏所在的轨道索引列表。
                                          (原版 deepjazz 使用 [0, 1, 6, 7])

    返回:
    chords_for_playback (stream.Stream): 用于后续音乐生成的原始伴奏轨道流。
    abstract_grammars (list[str]): 抽象语法字符串的列表。
    """
    
    print(f"正在从 '{data_fn}' 加载 MIDI 文件...")
    try:
        s = converter.parse(data_fn)
    except Exception as e:
        print(f"错误: 无法解析 MIDI 文件: {e}", file=sys.stderr)
        return None, None
        
    if not s.parts:
        print("错误: MIDI 文件不包含任何轨道 (Parts)。", file=sys.stderr)
        return None, None
        
    # --- 1. 提取旋律 (Melody) ---
    # 我们使用参数 `melody_part_index`，而不是硬编码的 5
    if melody_part_index >= len(s.parts):
        print(f"错误: 旋律轨道索引 {melody_part_index} 超出范围 (共 {len(s.parts)} 个轨道)。", file=sys.stderr)
        return None, None
        
    print(f"正在从轨道 {melody_part_index} 提取旋律...")
    # .flatten() 会解决所有原版脚本中遇到的 stream.Voice 嵌套问题
    melody_stream = s.parts[melody_part_index].flatten()
    
    # --- 2. 提取伴奏 (Accompaniment) 以供后续播放 ---
    # 这对应 `data_utils.py` 中 `generate_music` 的需要
    chords_for_playback = stream.Stream()
    print(f"正在从轨道 {accompaniment_part_indices} 提取伴奏 (用于播放)...")
    for i in accompaniment_part_indices:
        if i < len(s.parts):
            # .flatten() 确保我们只抓取音符与和弦
            chords_for_playback.mergeElements(s.parts[i].flatten())
        else:
            print(f"警告: 伴奏轨道索引 {i} 超出范围，已跳过。")

    # --- 3. 生成和弦分析 (Chord Analysis) 以供语法解析 ---
    # 这是最健壮的方法：`chordify()`
    # 它会分析 MIDI 中的 *所有* 轨道 (包括旋律) 来推导和声
    print("正在对整个乐曲进行和弦分析 (chordify)...")
    chord_analysis_stream = s.chordify()

    # --- 4. 生成抽象语法 ---
    # 我们传入“旋律流”和“和弦分析流”
    abstract_grammars = __get_abstract_grammars(melody_stream, chord_analysis_stream)

    # 返回 "用于播放的伴奏" 和 "抽象语法"
    # 这满足了 `data_utils.py` 和 `get_corpus_data` 的双重需求
    return chords_for_playback, abstract_grammars

def get_corpus_data(abstract_grammars):
    """
    (此函数与原版相同，功能正确且无需修改)
    
    从抽象语法列表创建语料库 (corpus) 和词典。
    """
    if not abstract_grammars:
        print("错误: 传入的 'abstract_grammars' 为空。", file=sys.stderr)
        return None, None, None, None
        
    print("正在从抽象语法创建语料库和词典...")
    
    # 1. 将所有小节的语法合并，并按空格分割成 token
    corpus = [token for measure_grammar in abstract_grammars 
                    for token in measure_grammar.split(' ')]
                    
    if not corpus:
        print("错误: 语料库为空，无法创建词典。可能是 'grammar.py' 未正确解析。", file=sys.stderr)
        return None, None, None, None

    # 2. 创建词汇表 (set of unique tokens)
    values = set(corpus)
    
    # 3. 创建 token <-> index 映射字典
    val_indices = dict((v, i) for i, v in enumerate(values))
    indices_val = dict((i, v) for i, v in enumerate(values))

    print(f"语料库创建完成。Token 总数: {len(corpus)}, 独立词汇表大小: {len(values)}")
    return corpus, values, val_indices, indices_val


# ------------------------------------------------------------------
# 示例用法 (main guard)
# ------------------------------------------------------------------
if __name__ == "__main__":
    """
    这是一个示例，展示如何使用这个新的 preprocess.py
    """
    # 假设你的文件路径
    data_file = 'data/original_metheny.mid' 
    
    # deepjazz 项目对 'original_metheny.mid' 使用的特定索引
    ORIGINAL_MELODY_INDEX = 5
    ORIGINAL_ACCOMP_INDICES = [0, 1, 6, 7]

    if not os.path.exists(data_file):
        print(f"错误: 找不到示例 MIDI 文件 '{data_file}'", file=sys.stderr)
        print("请从 deepjazz 项目下载 'original_metheny.mid' 并放入 'data' 文件夹", file=sys.stderr)
    else:
        # 1. 执行音乐数据处理
        # 我们传入 deepjazz 的特定轨道索引
        chords_playback, grammars = get_musical_data(
            data_file, 
            melody_part_index=ORIGINAL_MELODY_INDEX, 
            accompaniment_part_indices=ORIGINAL_ACCOMP_INDICES
        )
        
        if grammars:
            print("\n--- 成功！---")
            print(f"返回的 'chords_for_playback' 中的元素数量: {len(chords_playback)}")
            print(f"生成的 'abstract_grammars' 的小节数: {len(grammars)}")
            
            # 2. 执行语料库生成
            corpus, values, val_indices, indices_val = get_corpus_data(grammars)
            
            if corpus:
                print("\n--- 成功！---")
                print(f"第一个语法 token: {corpus[0]}")
                print(f"最后一个语法 token: {corpus[-1]}")
                print(f"Token '{corpus[0]}' 对应的索引: {val_indices[corpus[0]]}")