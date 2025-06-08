from editor.core import Editor

if __name__ == '__main__':
    editor = Editor()
    # Example: add two videos sequentially on layer 0
    editor.add_clip('video', 'intro.mp4', layer=0, start=0, end=5)
    editor.add_clip('video', 'main.mp4', layer=0, start=5, end=15)
    # Add background music
    editor.add_clip('audio', 'music.mp3', layer=1, start=0, end=20)
    # Fade in first video
    state1 = editor.apply_operation({'action': 'fade', 'params': {'layer': 0, 'index': 0, 'fade_type': 'in', 'duration': 1}})
    print(state1)
    # Render final
    editor.render('final_output.mp4')
