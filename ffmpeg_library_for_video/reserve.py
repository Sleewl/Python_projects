import ffmpeg

def reverse_and_rotate_video(input_file, output_file, rotate_mode):
    """
    Функция осуществляет реверс видео и аудио потоков, а затем поворот видео.

    :param input_file: Путь к входному видеофайлу (например, 'source.mp4').
    :param output_file: Путь для сохранения выходного видеофайла (например, 'output_video.mp4').
    :param rotate_mode: Режим поворота:
                        1 – Поворот на 90° по часовой стрелке;
                        2 – Поворот на 270° (или 90° против часовой);
                        3 – Поворот на 180°.
    """
    in_stream = ffmpeg.input(input_file)
    video_stream = in_stream.video
    audio_stream = in_stream.audio

    reversed_video = video_stream.filter('reverse')
    reversed_audio = audio_stream.filter('areverse')

    if rotate_mode == 1:
        rotated_video = reversed_video.filter('transpose', 1)
    elif rotate_mode == 2:
        rotated_video = reversed_video.filter('transpose', 2)
    elif rotate_mode == 3:
        rotated_video = reversed_video.filter('hflip').filter('vflip')
    else:
        raise ValueError("Неверный режим поворота. Допустимые значения: 1 (90°), 2 (270°), 3 (180°)")

    output_stream = ffmpeg.output(rotated_video, reversed_audio, output_file, pix_fmt='yuv420p')

    ffmpeg.run(output_stream)

if __name__ == '__main__':
    input_file = 'videoplayback.mp4'
    output_file = 'output_video.mp4'
    rotate_mode = 2

    try:
        reverse_and_rotate_video(input_file, output_file, rotate_mode)
        print(f"Обработка завершена. Выходной файл сохранён как: {output_file}")
    except Exception as e:
        print("Произошла ошибка при обработке видео:", e)
