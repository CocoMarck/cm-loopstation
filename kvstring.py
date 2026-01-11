kv = '''
#:import Window kivy.core.window.Window
#<BoxLayout>
    #size_hint_y: None
    #height: dp( min(Window.width, Window.height)*0.1 )
#<ScrollView>
    #size_hint_y: None
    #height: dp( min(Window.width, Window.height)*0.1 )


<Label>:
    font_size: min(Window.width, Window.height) * 0.05
<TextInput>
    font_size: min(Window.width, Window.height) * 0.05
<ToggleButton>:
    font_size: min(Window.width, Window.height) * 0.05


<LoopstationWindow>:
    record_button: record
    label_timer: timer_text
    label_tracks: tracks_text
    label_tracks_number: tracks_number
    label_record_bars: record_bars_text
    label_center: center_label

    label_bpm: text_bpm
    slider_bpm: bpm_slider


    grid_tracks: track_container

    button_play: play
    button_stop: stop
    button_restart: restart

    togglebutton_limit_record: limit_record
    togglebutton_play_beat: option_play_beat

    textinput_record_bars: record_bars
    slider_timer: timer_slider
    slider_beats: beats_slider

    metronome_container: metronome_box

    BoxLayout:
        width: root.width
        height: root.height*0.5
        y: root.height*0.5

        orientation: "vertical"

        # Fila 1
        ## circulos del Metronomo
        BoxLayout:
            id: metronome_box
            orientation: "horizontal"

        # Fila 2
        BoxLayout:
            orientation: "horizontal"

            ## timer
            BoxLayout:
                orientation: "horizontal"
                Label:
                    id: timer_text
                    text: "timer"
                Slider:
                    id: timer_slider

            ## Beats
            BoxLayout:
                orientation: "horizontal"
                Label:
                    text: "beats"
                Slider:
                    id: beats_slider

            ## BPM
            BoxLayout:
                orientation: "horizontal"
                Label:
                    id: text_bpm
                    text: "bpm"
                Slider:
                    id: bpm_slider

        # Fila 3
        BoxLayout:
            orientation: "horizontal"

            ## compases a grabar
            BoxLayout:
                orientation: "horizontal"
                Label:
                    id: record_bars_text
                    text: "bars"

                TextInput:
                    id: record_bars

            ## tracks
            BoxLayout:
                orientation: "horizontal"
                Label:
                    id: tracks_text
                    text: "tracks"
                Label:
                    id: tracks_number
                    text: "0"

        # Fila 4
        BoxLayout:
            ## Widgets
            orientation: "horizontal"

            # Col 1
            ToggleButton:
                id: option_play_beat
                text: "play beat"
                state: "down"

            ## Grabar
            ToggleButton:
                id: record
                text: "record"

            ## Opcion Parar grabación por numero de compass
            ToggleButton:
                id: limit_record
                text: "limit bars"

        BoxLayout:
            ## Widgets
            orientation: "horizontal"

            ## Opciones de reproducción de tracks
            Button:
                id: play
                text: 'play'

            Button:
                id: stop
                text: 'stop'

            Button:
                id: restart
                text: 'restart'


    # Segunda mitad de window
    # Scroll | Contenedor de Pistas
    ScrollView:
        width: root.width
        height: root.height*0.5
        y: 0
        do_scroll_x: True
        do_scroll_y: True

        # CheckBox Tracks
        GridLayout:
            id: track_container
            cols: 6

            size_hint_y: None
            height: self.minimum_height

            row_default_height: dp( min(Window.width, Window.height) * 0.1 )
            row_force_default: True

    # Timer
    FloatLayout:
        Label:
            id: center_label
            center_x: root.center_x
            center_y: root.center_y
            opacity: 1

'''
