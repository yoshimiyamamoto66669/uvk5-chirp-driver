
            # scanlists
            if _mem3.is_scanlist1 > 0 and _mem3.is_scanlist2 > 0:
                tmpscn = SCANLIST_LIST[3]  # "1+2"
            elif _mem3.is_scanlist1 > 0:
                tmpscn = SCANLIST_LIST[1]  # "1"
            elif _mem3.is_scanlist2 > 0:
                tmpscn = SCANLIST_LIST[2]  # "2"

        if is_empty:
            mem.empty = True
            # set some sane defaults:
            mem.power = UVK5_POWER_LEVELS[2]
            mem.extra = RadioSettingGroup("Extra", "extra")
            rs = RadioSetting("bclo", "BCLO", RadioSettingValueBoolean(False))
            mem.extra.append(rs)
            rs = RadioSetting("frev", "FreqRev",
                              RadioSettingValueBoolean(False))
            mem.extra.append(rs)
            rs = RadioSetting("pttid", "PTTID", RadioSettingValueList(
                PTTID_LIST, PTTID_LIST[0]))
            mem.extra.append(rs)
            rs = RadioSetting("dtmfdecode", "DTMF decode",
                              RadioSettingValueBoolean(False))
            mem.extra.append(rs)
            rs = RadioSetting("scrambler", "Scrambler", RadioSettingValueList(
                SCRAMBLER_LIST, SCRAMBLER_LIST[0]))
            mem.extra.append(rs)

            rs = RadioSetting("scanlists", "Scanlists", RadioSettingValueList(
                SCANLIST_LIST, SCANLIST_LIST[0]))
            mem.extra.append(rs)

            # actually the step and duplex are overwritten by chirp based on
            # bandplan. they are here to document sane defaults for IARU r1
            # mem.tuning_step = 25.0
            # mem.duplex = "off"

            return mem

        if number > 199:
            mem.name = VFO_CHANNEL_NAMES[number-200]
            mem.immutable = ["name", "scanlists"]
        else:
            _mem2 = self._memobj.channelname[number]
            for char in _mem2.name:
                if str(char) == "\xFF" or str(char) == "\x00":
                    break
                mem.name += str(char)
            mem.name = mem.name.rstrip()

        # Convert your low-level frequency to Hertz
        mem.freq = int(_mem.freq)*10
        mem.offset = int(_mem.offset)*10

        if (mem.offset == 0):
            mem.duplex = ''
        else:
            if _mem.shift == FLAGS1_OFFSET_MINUS:
                mem.duplex = '-'
            elif _mem.shift == FLAGS1_OFFSET_PLUS:
                mem.duplex = '+'
            else:
                mem.duplex = ''

        # tone data
        self._get_tone(mem, _mem)

        # mode
        if _mem.enable_am > 0:
            if _mem.bandwidth > 0:
                mem.mode = "NAM"
            else:
                mem.mode = "AM"
        else:
            if _mem.bandwidth > 0:
                mem.mode = "NFM"
            else:
                mem.mode = "FM"

        # tuning step
        tstep = _mem.step & 0x7
        if tstep < len(STEPS):
            mem.tuning_step = STEPS[tstep]
        else:
            mem.tuning_step = 2.5

        # power
        if _mem.txpower == POWER_HIGH:
            mem.power = UVK5_POWER_LEVELS[2]
        elif _mem.txpower == POWER_MEDIUM:
            mem.power = UVK5_POWER_LEVELS[1]
        else:
            mem.power = UVK5_POWER_LEVELS[0]

        # We'll consider any blank (i.e. 0MHz frequency) to be empty
        if (_mem.freq == 0xffffffff) or (_mem.freq == 0):
            mem.empty = True
        else:
            mem.empty = False

        mem.extra = RadioSettingGroup("Extra", "extra")

        # BCLO
        is_bclo = bool(_mem.bclo > 0)
        rs = RadioSetting("bclo", "BCLO", RadioSettingValueBoolean(is_bclo))
        mem.extra.append(rs)
        tmpcomment += "BCLO:"+(is_bclo and "ON" or "off")+" "

        # Frequency reverse - whatever that means, don't see it in the manual
        is_frev = bool(_mem.freq_reverse > 0)
        rs = RadioSetting("frev", "FreqRev", RadioSettingValueBoolean(is_frev))
        mem.extra.append(rs)
        tmpcomment += "FreqReverse:"+(is_frev and "ON" or "off")+" "

        # PTTID
        pttid = _mem.dtmf_pttid
        rs = RadioSetting("pttid", "PTTID", RadioSettingValueList(
            PTTID_LIST, PTTID_LIST[pttid]))
        mem.extra.append(rs)
        tmpcomment += "PTTid:"+PTTID_LIST[pttid]+" "

        # DTMF DECODE
        is_dtmf = bool(_mem.dtmf_decode > 0)
        rs = RadioSetting("dtmfdecode", "DTMF decode",
                          RadioSettingValueBoolean(is_dtmf))
        mem.extra.append(rs)
        tmpcomment += "DTMFdecode:"+(is_dtmf and "ON" or "off")+" "

        # Scrambler
        if _mem.scrambler & 0x0f < len(SCRAMBLER_LIST):
            enc = _mem.scrambler & 0x0f
        else:
            enc = 0

        rs = RadioSetting("scrambler", "Scrambler", RadioSettingValueList(
            SCRAMBLER_LIST, SCRAMBLER_LIST[enc]))
        mem.extra.append(rs)
        tmpcomment += "Scrambler:"+SCRAMBLER_LIST[enc]+" "

        rs = RadioSetting("scanlists", "Scanlists", RadioSettingValueList(
            SCANLIST_LIST, tmpscn))
        mem.extra.append(rs)

        return mem

    def set_settings(self, settings):
        _mem = self._memobj
        for element in settings:
            if not isinstance(element, RadioSetting):
                self.set_settings(element)
                continue

            # basic settings

            # call channel
            if element.get_name() == "call_channel":
                _mem.call_channel = int(element.value)-1

            # squelch
            if element.get_name() == "squelch":
                _mem.squelch = int(element.value)
            # TOT
            if element.get_name() == "tot":
                _mem.max_talk_time = int(element.value)

            # NOAA autoscan
            if element.get_name() == "noaa_autoscan":
                _mem.noaa_autoscan = element.value and 1 or 0

            # VOX switch
            if element.get_name() == "vox_switch":
                _mem.vox_switch = element.value and 1 or 0

            # vox level
            if element.get_name() == "vox_level":
                _mem.vox_level = int(element.value)-1

            # mic gain
            if element.get_name() == "mic_gain":
                _mem.mic_gain = int(element.value)

            # Channel display mode
            if element.get_name() == "channel_display_mode":
                _mem.channel_display_mode = CHANNELDISP_LIST.index(
                    str(element.value))

            # Crossband receiving/transmitting
            if element.get_name() == "crossband":
                _mem.crossband = CROSSBAND_LIST.index(str(element.value))

            # Battery Save
            if element.get_name() == "battery_save":
                _mem.battery_save = BATSAVE_LIST.index(str(element.value))
            # Dual Watch
            if element.get_name() == "dualwatch":
                _mem.dual_watch = DUALWATCH_LIST.index(str(element.value))

            # Backlight auto mode
            if element.get_name() == "backlight_auto_mode":
                _mem.backlight_auto_mode = \
                        BACKLIGHT_LIST.index(str(element.value))

            # Tail tone elimination
            if element.get_name() == "tail_note_elimination":
                _mem.tail_note_elimination = element.value and 1 or 0

            # VFO Open
            if element.get_name() == "vfo_open":
                _mem.vfo_open = element.value and 1 or 0

            # Beep control
            if element.get_name() == "beep_control":
                _mem.beep_control = element.value and 1 or 0

            # Scan resume mode
            if element.get_name() == "scan_resume_mode":
                _mem.scan_resume_mode = SCANRESUME_LIST.index(
                    str(element.value))

            # Keypad lock
            if element.get_name() == "key_lock":
                _mem.key_lock = element.value and 1 or 0

            # Auto keypad lock
            if element.get_name() == "auto_keypad_lock":
                _mem.auto_keypad_lock = element.value and 1 or 0

            # Power on display mode
            if element.get_name() == "welcome_mode":
                _mem.power_on_dispmode = WELCOME_LIST.index(str(element.value))

            # Keypad Tone
            if element.get_name() == "keypad_tone":
                _mem.keypad_tone = KEYPADTONE_LIST.index(str(element.value))

            # Language
            if element.get_name() == "language":
                _mem.language = LANGUAGE_LIST.index(str(element.value))

            # Alarm mode
            if element.get_name() == "alarm_mode":
                _mem.alarm_mode = ALARMMODE_LIST.index(str(element.value))

            # Reminding of end of talk
            if element.get_name() == "reminding_of_end_talk":
                _mem.reminding_of_end_talk = REMENDOFTALK_LIST.index(
                    str(element.value))

            # Repeater tail tone elimination
            if element.get_name() == "repeater_tail_elimination":
                _mem.repeater_tail_elimination = RTE_LIST.index(
                    str(element.value))

            # Logo string 1
            if element.get_name() == "logo1":
                b = str(element.value).rstrip("\x20\xff\x00")+"\x00"*12
                _mem.logo_line1 = b[0:12]+"\x00\xff\xff\xff"

            # Logo string 2
            if element.get_name() == "logo2":
                b = str(element.value).rstrip("\x20\xff\x00")+"\x00"*12
                _mem.logo_line2 = b[0:12]+"\x00\xff\xff\xff"

            # unlock settings

            # FLOCK
            if element.get_name() == "flock":
                _mem.int_flock = FLOCK_LIST.index(str(element.value))

            # 350TX
            if element.get_name() == "350tx":
                _mem.int_350tx = element.value and 1 or 0

            # 200TX
            if element.get_name() == "200tx":
                _mem.int_200tx = element.value and 1 or 0

            # 500TX
            if element.get_name() == "500tx":
                _mem.int_500tx = element.value and 1 or 0

            # 350EN
            if element.get_name() == "350en":
                _mem.int_350en = element.value and 1 or 0

            # SCREN
            if element.get_name() == "scren":
                _mem.int_scren = element.value and 1 or 0

            # fm radio
            for i in range(1, 21):
                freqname = "FM_" + str(i)
                if element.get_name() == freqname:
                    val = str(element.value).strip()
                    try:
                        val2 = int(float(val)*10)
                    except Exception:
                        val2 = 0xffff

                    if val2 < FMMIN*10 or val2 > FMMAX*10:
                        val2 = 0xffff
#                        raise errors.InvalidValueError(
#                                "FM radio frequency should be a value "
#                                "in the range %.1f - %.1f" % (FMMIN , FMMAX))
                    _mem.fmfreq[i-1] = val2

            # dtmf settings
            if element.get_name() == "dtmf_side_tone":
                _mem.dtmf_settings.side_tone = \
                        element.value and 1 or 0

            if element.get_name() == "dtmf_separate_code":
                _mem.dtmf_settings.separate_code = str(element.value)

            if element.get_name() == "dtmf_group_call_code":
                _mem.dtmf_settings.group_call_code = element.value

            if element.get_name() == "dtmf_decode_response":
                _mem.dtmf_settings.decode_response = \
                        DTMF_DECODE_RESPONSE_LIST.index(str(element.value))

            if element.get_name() == "dtmf_auto_reset_time":
                _mem.dtmf_settings.auto_reset_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_preload_time":
                _mem.dtmf_settings.preload_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_first_code_persist_time":
                _mem.dtmf_settings.first_code_persist_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_hash_persist_time":
                _mem.dtmf_settings.hash_persist_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_code_persist_time":
                _mem.dtmf_settings.code_persist_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_code_interval_time":
                _mem.dtmf_settings.code_interval_time = \
                        int(int(element.value)/10)

            if element.get_name() == "dtmf_permit_remote_kill":
                _mem.dtmf_settings.permit_remote_kill = \
                        element.value and 1 or 0

            if element.get_name() == "dtmf_dtmf_local_code":
                k = str(element.value).rstrip("\x20\xff\x00") + "\x00"*3
                _mem.dtmf_settings_numbers.dtmf_local_code = k[0:3]

            if element.get_name() == "dtmf_dtmf_up_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00"*16
                _mem.dtmf_settings_numbers.dtmf_up_code = k[0:16]

            if element.get_name() == "dtmf_dtmf_down_code":
                k = str(element.value).rstrip("\x20\xff\x00") + "\x00"*16
                _mem.dtmf_settings_numbers.dtmf_down_code = k[0:16]

            if element.get_name() == "dtmf_kill_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00"*5
                _mem.dtmf_settings_numbers.kill_code = k[0:5]

            if element.get_name() == "dtmf_revive_code":
                k = str(element.value).strip("\x20\xff\x00") + "\x00"*5
                _mem.dtmf_settings_numbers.revive_code = k[0:5]

            # dtmf contacts
            for i in range(1, 17):
                varname = "DTMF_" + str(i)
                if element.get_name() == varname:
                    k = str(element.value).rstrip("\x20\xff\x00") + "\x00"*8
                    _mem.dtmfcontact[i-1].name = k[0:8]

                varnumname = "DTMFNUM_" + str(i)
                if element.get_name() == varnumname:
                    k = str(element.value).rstrip("\x20\xff\x00") + "\xff"*3
                    _mem.dtmfcontact[i-1].number = k[0:3]

            # scanlist stuff
            if element.get_name() == "scanlist_default":
                val = (int(element.value) == 2) and 1 or 0
                _mem.scanlist_default = val

            if element.get_name() == "scanlist1_priority_scan":
                _mem.scanlist1_priority_scan = \
                        element.value and 1 or 0

            if element.get_name() == "scanlist2_priority_scan":
                _mem.scanlist2_priority_scan = \
                        element.value and 1 or 0

            if element.get_name() == "scanlist1_priority_ch1" or \
                    element.get_name() == "scanlist1_priority_ch2" or \
                    element.get_name() == "scanlist2_priority_ch1" or \
                    element.get_name() == "scanlist2_priority_ch2":

                val = int(element.value)

                if val > 200 or val < 1:
                    val = 0xff
                else:
                    val -= 1

                if element.get_name() == "scanlist1_priority_ch1":
                    _mem.scanlist1_priority_ch1 = val
                if element.get_name() == "scanlist1_priority_ch2":
                    _mem.scanlist1_priority_ch2 = val
                if element.get_name() == "scanlist2_priority_ch1":
                    _mem.scanlist2_priority_ch1 = val
                if element.get_name() == "scanlist2_priority_ch2":
                    _mem.scanlist2_priority_ch2 = val

            if element.get_name() == "key1_shortpress_action":
                _mem.key1_shortpress_action = KEYACTIONS_LIST.index(
                        str(element.value))

            if element.get_name() == "key1_longpress_action":
                _mem.key1_longpress_action = KEYACTIONS_LIST.index(
                        str(element.value))

            if element.get_name() == "key2_shortpress_action":
                _mem.key2_shortpress_action = KEYACTIONS_LIST.index(
                        str(element.value))

            if element.get_name() == "key2_longpress_action":
                _mem.key2_longpress_action = KEYACTIONS_LIST.index(
                        str(element.value))

    def get_settings(self):
        _mem = self._memobj
        basic = RadioSettingGroup("basic", "Basic Settings")
        keya = RadioSettingGroup("keya", "Programmable keys")
        dtmf = RadioSettingGroup("dtmf", "DTMF Settings")
        dtmfc = RadioSettingGroup("dtmfc", "DTMF Contacts")
        scanl = RadioSettingGroup("scn", "Scan Lists")
        unlock = RadioSettingGroup("unlock", "Unlock Settings")
        fmradio = RadioSettingGroup("fmradio", "FM Radio")

        roinfo = RadioSettingGroup("roinfo", "Driver information")

        top = RadioSettings(
                basic, keya, dtmf, dtmfc, scanl, unlock, fmradio, roinfo)

        # Programmable keys
        tmpval = int(_mem.key1_shortpress_action)
        if tmpval >= len(KEYACTIONS_LIST):
            tmpval = 0
        rs = RadioSetting("key1_shortpress_action", "Side key 1 short press",
                          RadioSettingValueList(
                              KEYACTIONS_LIST, KEYACTIONS_LIST[tmpval]))
        keya.append(rs)

        tmpval = int(_mem.key1_longpress_action)
        if tmpval >= len(KEYACTIONS_LIST):
            tmpval = 0
        rs = RadioSetting("key1_longpress_action", "Side key 1 long press",
                          RadioSettingValueList(
                              KEYACTIONS_LIST, KEYACTIONS_LIST[tmpval]))
        keya.append(rs)

        tmpval = int(_mem.key2_shortpress_action)
        if tmpval >= len(KEYACTIONS_LIST):
            tmpval = 0
        rs = RadioSetting("key2_shortpress_action", "Side key 2 short press",
                          RadioSettingValueList(
                              KEYACTIONS_LIST, KEYACTIONS_LIST[tmpval]))
        keya.append(rs)

        tmpval = int(_mem.key2_longpress_action)
        if tmpval >= len(KEYACTIONS_LIST):
            tmpval = 0
        rs = RadioSetting("key2_longpress_action", "Side key 2 long press",
                          RadioSettingValueList(
                              KEYACTIONS_LIST, KEYACTIONS_LIST[tmpval]))
        keya.append(rs)

        # DTMF settings
        tmppr = bool(_mem.dtmf_settings.side_tone > 0)
        rs = RadioSetting(
                "dtmf_side_tone",
                "DTMF Sidetone",
                RadioSettingValueBoolean(tmppr))
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings.separate_code)
        if tmpval not in DTMF_CODE_CHARS:
            tmpval = '*'
        val = RadioSettingValueString(1, 1, tmpval)
        val.set_charset(DTMF_CODE_CHARS)
        rs = RadioSetting("dtmf_separate_code", "Separate Code", val)
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings.group_call_code)
        if tmpval not in DTMF_CODE_CHARS:
            tmpval = '#'
        val = RadioSettingValueString(1, 1, tmpval)
        val.set_charset(DTMF_CODE_CHARS)
        rs = RadioSetting("dtmf_group_call_code", "Group Call Code", val)
        dtmf.append(rs)

        tmpval = _mem.dtmf_settings.decode_response
        if tmpval >= len(DTMF_DECODE_RESPONSE_LIST):
            tmpval = 0
        rs = RadioSetting("dtmf_decode_response", "Decode Response",
                          RadioSettingValueList(
                              DTMF_DECODE_RESPONSE_LIST,
                              DTMF_DECODE_RESPONSE_LIST[tmpval]))
        dtmf.append(rs)

        tmpval = _mem.dtmf_settings.auto_reset_time
        if tmpval > 60 or tmpval < 5:
            tmpval = 5
        rs = RadioSetting("dtmf_auto_reset_time",
                          "Auto reset time (s)",
                          RadioSettingValueInteger(5, 60, tmpval))
        dtmf.append(rs)

        tmpval = int(_mem.dtmf_settings.preload_time)
        if tmpval > 100 or tmpval < 3:
            tmpval = 30
        tmpval *= 10
        rs = RadioSetting("dtmf_preload_time",
                          "Pre-load time (ms)",
                          RadioSettingValueInteger(30, 1000, tmpval, 10))
        dtmf.append(rs)

        tmpval = int(_mem.dtmf_settings.first_code_persist_time)
        if tmpval > 100 or tmpval < 3:
            tmpval = 30
        tmpval *= 10
        rs = RadioSetting("dtmf_first_code_persist_time",
                          "First code persist time (ms)",
                          RadioSettingValueInteger(30, 1000, tmpval, 10))
        dtmf.append(rs)

        tmpval = int(_mem.dtmf_settings.hash_persist_time)
        if tmpval > 100 or tmpval < 3:
            tmpval = 30
        tmpval *= 10
        rs = RadioSetting("dtmf_hash_persist_time",
                          "#/* persist time (ms)",
                          RadioSettingValueInteger(30, 1000, tmpval, 10))
        dtmf.append(rs)

        tmpval = int(_mem.dtmf_settings.code_persist_time)
        if tmpval > 100 or tmpval < 3:
            tmpval = 30
        tmpval *= 10
        rs = RadioSetting("dtmf_code_persist_time",
                          "Code persist time (ms)",
                          RadioSettingValueInteger(30, 1000, tmpval, 10))
        dtmf.append(rs)

        tmpval = int(_mem.dtmf_settings.code_interval_time)
        if tmpval > 100 or tmpval < 3:
            tmpval = 30
        tmpval *= 10
        rs = RadioSetting("dtmf_code_interval_time",
                          "Code interval time (ms)",
                          RadioSettingValueInteger(30, 1000, tmpval, 10))
        dtmf.append(rs)

        tmpval = bool(_mem.dtmf_settings.permit_remote_kill > 0)
        rs = RadioSetting(
                "dtmf_permit_remote_kill",
                "Permit remote kill",
                RadioSettingValueBoolean(tmpval))
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings_numbers.dtmf_local_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_ID:
                continue
            else:
                tmpval = "103"
                break
        val = RadioSettingValueString(3, 3, tmpval)
        val.set_charset(DTMF_CHARS_ID)
        rs = RadioSetting("dtmf_dtmf_local_code",
                          "Local code (3 chars 0-9 ABCD)", val)
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings_numbers.dtmf_up_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_UPDOWN or i == "":
                continue
            else:
                tmpval = "123"
                break
        val = RadioSettingValueString(1, 16, tmpval)
        val.set_charset(DTMF_CHARS_UPDOWN)
        rs = RadioSetting("dtmf_dtmf_up_code",
                          "Up code (1-16 chars 0-9 ABCD*#)", val)
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings_numbers.dtmf_down_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_UPDOWN:
                continue
            else:
                tmpval = "456"
                break
        val = RadioSettingValueString(1, 16, tmpval)
        val.set_charset(DTMF_CHARS_UPDOWN)
        rs = RadioSetting("dtmf_dtmf_down_code",
                          "Down code (1-16 chars 0-9 ABCD*#)", val)
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings_numbers.kill_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_KILL:
                continue
            else:
                tmpval = "77777"
                break
        if not len(tmpval) == 5:
            tmpval = "77777"
        val = RadioSettingValueString(5, 5, tmpval)
        val.set_charset(DTMF_CHARS_KILL)
        rs = RadioSetting("dtmf_kill_code",
                          "Kill code (5 chars 0-9 ABCD)", val)
        dtmf.append(rs)

        tmpval = str(_mem.dtmf_settings_numbers.revive_code).upper().strip(
                "\x00\xff\x20")
        for i in tmpval:
            if i in DTMF_CHARS_KILL:
                continue
            else:
                tmpval = "88888"
                break
        if not len(tmpval) == 5:
            tmpval = "88888"
        val = RadioSettingValueString(5, 5, tmpval)
        val.set_charset(DTMF_CHARS_KILL)
        rs = RadioSetting("dtmf_revive_code",
                          "Revive code (5 chars 0-9 ABCD)", val)
        dtmf.append(rs)

        val = RadioSettingValueString(0, 80,
                                      "All DTMF Contacts are 3 codes "
                                      "(valid: 0-9 * # ABCD), "
                                      "or an empty string")
        val.set_mutable(False)
        rs = RadioSetting("dtmf_descr1", "DTMF Contacts", val)
        dtmfc.append(rs)

        for i in range(1, 17):
            varname = "DTMF_"+str(i)
            varnumname = "DTMFNUM_"+str(i)
            vardescr = "DTMF Contact "+str(i)+" name"
            varinumdescr = "DTMF Contact "+str(i)+" number"

            cntn = str(_mem.dtmfcontact[i-1].name).strip("\x20\x00\xff")
            cntnum = str(_mem.dtmfcontact[i-1].number).strip("\x20\x00\xff")

            val = RadioSettingValueString(0, 8, cntn)
            rs = RadioSetting(varname, vardescr, val)
            dtmfc.append(rs)

            val = RadioSettingValueString(0, 3, cntnum)
            val.set_charset(DTMF_CHARS)
            rs = RadioSetting(varnumname, varinumdescr, val)
            dtmfc.append(rs)

        # scanlists
        if _mem.scanlist_default == 1:
            tmpsc = 2
        else:
            tmpsc = 1
        rs = RadioSetting("scanlist_default",
                          "Default scanlist",
                          RadioSettingValueInteger(1, 2, tmpsc))
        scanl.append(rs)

        tmppr = bool((_mem.scanlist1_priority_scan & 1) > 0)
        rs = RadioSetting(
                "scanlist1_priority_scan",
                "Scanlist 1 priority channel scan",
                RadioSettingValueBoolean(tmppr))
        scanl.append(rs)

        tmpch = _mem.scanlist1_priority_ch1 + 1
        if tmpch > 200:
            tmpch = 0
        rs = RadioSetting("scanlist1_priority_ch1",
                          "Scanlist 1 priority channel 1 (0 - off)",
                          RadioSettingValueInteger(0, 200, tmpch))
        scanl.append(rs)

        tmpch = _mem.scanlist1_priority_ch2 + 1
        if tmpch > 200:
            tmpch = 0
        rs = RadioSetting("scanlist1_priority_ch2",
                          "Scanlist 1 priority channel 2 (0 - off)",
                          RadioSettingValueInteger(0, 200, tmpch))
        scanl.append(rs)

        tmppr = bool((_mem.scanlist2_priority_scan & 1) > 0)
        rs = RadioSetting(
                "scanlist2_priority_scan",
                "Scanlist 2 priority channel scan",
                RadioSettingValueBoolean(tmppr))
        scanl.append(rs)

        tmpch = _mem.scanlist2_priority_ch1 + 1
        if tmpch > 200:
            tmpch = 0
        rs = RadioSetting("scanlist2_priority_ch1",
                          "Scanlist 2 priority channel 1 (0 - off)",
                          RadioSettingValueInteger(0, 200, tmpch))
        scanl.append(rs)

        tmpch = _mem.scanlist2_priority_ch2 + 1
        if tmpch > 200:
            tmpch = 0
        rs = RadioSetting("scanlist2_priority_ch2",
                          "Scanlist 2 priority channel 2 (0 - off)",
                          RadioSettingValueInteger(0, 200, tmpch))
        scanl.append(rs)

        # basic settings

        # call channel
        tmpc = _mem.call_channel+1
        if tmpc > 200:
            tmpc = 1
        rs = RadioSetting("call_channel", "One key call channel",
                          RadioSettingValueInteger(1, 200, tmpc))
        basic.append(rs)

        # squelch
        tmpsq = _mem.squelch
        if tmpsq > 9:
            tmpsq = 1
        rs = RadioSetting("squelch", "Squelch",
                          RadioSettingValueInteger(0, 9, tmpsq))
        basic.append(rs)

        # TOT
        tmptot = _mem.max_talk_time
        if tmptot > 10:
            tmptot = 10
        rs = RadioSetting(
                "tot",
                "Max talk time [min]",
                RadioSettingValueInteger(0, 10, tmptot))
        basic.append(rs)

        # NOAA autoscan
        rs = RadioSetting(
                "noaa_autoscan",
                "NOAA Autoscan", RadioSettingValueBoolean(
                    bool(_mem.noaa_autoscan > 0)))
        basic.append(rs)

        # VOX switch
        rs = RadioSetting(
                "vox_switch",
                "VOX enabled", RadioSettingValueBoolean(
                    bool(_mem.vox_switch > 0)))
        basic.append(rs)

        # VOX Level
        tmpvox = _mem.vox_level+1
        if tmpvox > 10:
            tmpvox = 10
        rs = RadioSetting("vox_level", "VOX Level",
                          RadioSettingValueInteger(1, 10, tmpvox))
        basic.append(rs)

        # Mic gain
        tmpmicgain = _mem.mic_gain
        if tmpmicgain > 4:
            tmpmicgain = 4
        rs = RadioSetting("mic_gain", "Mic Gain",
                          RadioSettingValueInteger(0, 4, tmpmicgain))
        basic.append(rs)

        # Channel display mode
        tmpchdispmode = _mem.channel_display_mode
        if tmpchdispmode >= len(CHANNELDISP_LIST):
            tmpchdispmode = 0
        rs = RadioSetting(
                "channel_display_mode",
                "Channel display mode",
                RadioSettingValueList(
                    CHANNELDISP_LIST,
                    CHANNELDISP_LIST[tmpchdispmode]))
        basic.append(rs)

        # Crossband receiving/transmitting
        tmpcross = _mem.crossband
        if tmpcross >= len(CROSSBAND_LIST):
            tmpcross = 0
        rs = RadioSetting(
                "crossband",
                "Cross-band receiving/transmitting",
                RadioSettingValueList(
                    CROSSBAND_LIST,
                    CROSSBAND_LIST[tmpcross]))
        basic.append(rs)

        # Battery save
        tmpbatsave = _mem.battery_save
        if tmpbatsave >= len(BATSAVE_LIST):
            tmpbatsave = BATSAVE_LIST.index("1:4")
        rs = RadioSetting(
                "battery_save",
                "Battery Save",
                RadioSettingValueList(
                    BATSAVE_LIST,
                    BATSAVE_LIST[tmpbatsave]))
        basic.append(rs)

        # Dual watch
        tmpdual = _mem.dual_watch
        if tmpdual >= len(DUALWATCH_LIST):
            tmpdual = 0
        rs = RadioSetting("dualwatch", "Dual Watch", RadioSettingValueList(
            DUALWATCH_LIST, DUALWATCH_LIST[tmpdual]))
        basic.append(rs)

        # Backlight auto mode
        tmpback = _mem.backlight_auto_mode
        if tmpback >= len(BACKLIGHT_LIST):
            tmpback = 0
        rs = RadioSetting("backlight_auto_mode",
                          "Backlight auto mode",
                          RadioSettingValueList(
                              BACKLIGHT_LIST,
                              BACKLIGHT_LIST[tmpback]))
        basic.append(rs)

        # Tail tone elimination
        rs = RadioSetting(
                "tail_note_elimination",
                "Tail tone elimination",
                RadioSettingValueBoolean(
                    bool(_mem.tail_note_elimination > 0)))
        basic.append(rs)

        # VFO open
        rs = RadioSetting("vfo_open", "VFO open",
                          RadioSettingValueBoolean(bool(_mem.vfo_open > 0)))
        basic.append(rs)

        # Beep control
        rs = RadioSetting(
                "beep_control",
                "Beep control",
                RadioSettingValueBoolean(bool(_mem.beep_control > 0)))
        basic.append(rs)

        # Scan resume mode
        tmpscanres = _mem.scan_resume_mode
        if tmpscanres >= len(SCANRESUME_LIST):
            tmpscanres = 0
        rs = RadioSetting(
                "scan_resume_mode",
                "Scan resume mode",
                RadioSettingValueList(
                    SCANRESUME_LIST,
                    SCANRESUME_LIST[tmpscanres]))
        basic.append(rs)

        # Keypad locked
        rs = RadioSetting(
                "key_lock",
                "Keypad lock",
                RadioSettingValueBoolean(bool(_mem.key_lock > 0)))
        basic.append(rs)

        # Auto keypad lock
        rs = RadioSetting(
                "auto_keypad_lock",
                "Auto keypad lock",
                RadioSettingValueBoolean(bool(_mem.auto_keypad_lock > 0)))
        basic.append(rs)

        # Power on display mode
        tmpdispmode = _mem.power_on_dispmode
        if tmpdispmode >= len(WELCOME_LIST):
            tmpdispmode = 0
        rs = RadioSetting(
                "welcome_mode",
                "Power on display mode",
                RadioSettingValueList(
                    WELCOME_LIST,
                    WELCOME_LIST[tmpdispmode]))
        basic.append(rs)

        # Keypad Tone
        tmpkeypadtone = _mem.keypad_tone
        if tmpkeypadtone >= len(KEYPADTONE_LIST):
            tmpkeypadtone = 0
        rs = RadioSetting("keypad_tone", "Keypad tone", RadioSettingValueList(
            KEYPADTONE_LIST, KEYPADTONE_LIST[tmpkeypadtone]))
        basic.append(rs)

        # Language
        tmplanguage = _mem.language
        if tmplanguage >= len(LANGUAGE_LIST):
            tmplanguage = 0
        rs = RadioSetting("language", "Language", RadioSettingValueList(
            LANGUAGE_LIST, LANGUAGE_LIST[tmplanguage]))
        basic.append(rs)

        # Alarm mode
        tmpalarmmode = _mem.alarm_mode
        if tmpalarmmode >= len(ALARMMODE_LIST):
            tmpalarmmode = 0
        rs = RadioSetting("alarm_mode", "Alarm mode", RadioSettingValueList(
            ALARMMODE_LIST, ALARMMODE_LIST[tmpalarmmode]))
        basic.append(rs)

        # Reminding of end of talk
        tmpalarmmode = _mem.reminding_of_end_talk
        if tmpalarmmode >= len(REMENDOFTALK_LIST):
            tmpalarmmode = 0
        rs = RadioSetting(
                "reminding_of_end_talk",
                "Reminding of end of talk",
                RadioSettingValueList(
                    REMENDOFTALK_LIST,
                    REMENDOFTALK_LIST[tmpalarmmode]))
        basic.append(rs)

        # Repeater tail tone elimination
        tmprte = _mem.repeater_tail_elimination
        if tmprte >= len(RTE_LIST):
            tmprte = 0
        rs = RadioSetting(
                "repeater_tail_elimination",
                "Repeater tail tone elimination",
                RadioSettingValueList(RTE_LIST, RTE_LIST[tmprte]))
        basic.append(rs)

        # Logo string 1
        logo1 = str(_mem.logo_line1).strip("\x20\x00\xff") + "\x00"
        logo1 = _getstring(logo1.encode('ascii', errors='ignore'), 0, 12)
        rs = RadioSetting("logo1", "Logo string 1 (12 characters)",
                          RadioSettingValueString(0, 12, logo1))
        basic.append(rs)

        # Logo string 2
        logo2 = str(_mem.logo_line2).strip("\x20\x00\xff") + "\x00"
        logo2 = _getstring(logo2.encode('ascii', errors='ignore'), 0, 12)
        rs = RadioSetting("logo2", "Logo string 2 (12 characters)",
                          RadioSettingValueString(0, 12, logo2))
        basic.append(rs)

        # FM radio
        for i in range(1, 21):
            freqname = "FM_"+str(i)
            fmfreq = _mem.fmfreq[i-1]/10.0
            if fmfreq < FMMIN or fmfreq > FMMAX:
                rs = RadioSetting(freqname, freqname,
                                  RadioSettingValueString(0, 5, ""))
            else:
                rs = RadioSetting(freqname, freqname,
                                  RadioSettingValueString(0, 5, str(fmfreq)))

            fmradio.append(rs)

        # unlock settings

        # F-LOCK
        tmpflock = _mem.int_flock
        if tmpflock >= len(FLOCK_LIST):
            tmpflock = 0
        rs = RadioSetting(
            "flock", "F-LOCK",
            RadioSettingValueList(FLOCK_LIST, FLOCK_LIST[tmpflock]))
        unlock.append(rs)

        # 350TX
        rs = RadioSetting("350tx", "350TX - unlock 350-400MHz TX",
                          RadioSettingValueBoolean(
                              bool(_mem.int_350tx > 0)))
        unlock.append(rs)

        # 200TX
        rs = RadioSetting("200tx", "200TX - unlock 174-350MHz TX",
                          RadioSettingValueBoolean(
                              bool(_mem.int_200tx > 0)))
        unlock.append(rs)

        # 500TX
        rs = RadioSetting("500tx", "500TX - unlock 500-600MHz TX",
                          RadioSettingValueBoolean(
                              bool(_mem.int_500tx > 0)))
        unlock.append(rs)

        # 350EN
        rs = RadioSetting("350en", "350EN - unlock 350-400MHz RX",
                          RadioSettingValueBoolean(
                              bool(_mem.int_350en > 0)))
        unlock.append(rs)

        # SCREEN
        rs = RadioSetting("scren", "SCREN - scrambler enable",
                          RadioSettingValueBoolean(
                              bool(_mem.int_scren > 0)))
        unlock.append(rs)

        # readonly info
        # Firmware
        if self.FIRMWARE_VERSION == "":
            firmware = "To get the firmware version please download"
            "the image from the radio first"
        else:
            firmware = self.FIRMWARE_VERSION

        val = RadioSettingValueString(0, 128, firmware)
        val.set_mutable(False)
        rs = RadioSetting("fw_ver", "Firmware Version", val)
        roinfo.append(rs)

        # TODO: remove showing the driver version when it's in mainline chirp
        # Driver version
        val = RadioSettingValueString(0, 128, DRIVER_VERSION)
        val.set_mutable(False)
        rs = RadioSetting("driver_ver", "Driver version", val)
        roinfo.append(rs)

        # No limits version for hacked firmware
        val = RadioSettingValueBoolean(self.FIRMWARE_NOLIMITS)
        val.set_mutable(False)
        rs = RadioSetting("nolimits", "Limits disabled for modified firmware",
                          val)
        roinfo.append(rs)

        return top

    # Store details about a high-level memory to the memory map
    # This is called when a user edits a memory in the UI
    def set_memory(self, mem):
        number = mem.number-1

        # Get a low-level memory object mapped to the image
        _mem = self._memobj.channel[number]
        _mem4 = self._memobj
        # empty memory
        if mem.empty:
            _mem.set_raw("\xFF" * 16)
            if number < 200:
                _mem2 = self._memobj.channelname[number]
                _mem2.set_raw("\xFF" * 16)
                _mem4.channel_attributes[number].is_scanlist1 = 0
                _mem4.channel_attributes[number].is_scanlist2 = 0
                _mem4.channel_attributes[number].unknown1 = 0
                _mem4.channel_attributes[number].unknown2 = 0
                _mem4.channel_attributes[number].is_free = 1
                _mem4.channel_attributes[number].band = 0x7
            return mem

        # clean the channel memory, restore some bits if it was used before
        if _mem.get_raw()[0] == "\xff":
            # this was an empty memory
            _mem.set_raw("\x00" * 16)
        else:
            # this memory was't empty, save some bits that we don't know the
            # meaning of, or that we don't support yet
            prev_0a = _mem.get_raw(asbytes=True)[0x0a] & SAVE_MASK_0A
            prev_0b = _mem.get_raw(asbytes=True)[0x0b] & SAVE_MASK_0B
            prev_0c = _mem.get_raw(asbytes=True)[0x0c] & SAVE_MASK_0C
            prev_0d = _mem.get_raw(asbytes=True)[0x0d] & SAVE_MASK_0D
            prev_0e = _mem.get_raw(asbytes=True)[0x0e] & SAVE_MASK_0E
            prev_0f = _mem.get_raw(asbytes=True)[0x0f] & SAVE_MASK_0F
            _mem.set_raw("\x00" * 10 +
                         chr(prev_0a) + chr(prev_0b) + chr(prev_0c) +
                         chr(prev_0d) + chr(prev_0e) + chr(prev_0f))

        if number < 200:
            _mem4.channel_attributes[number].is_scanlist1 = 0
            _mem4.channel_attributes[number].is_scanlist2 = 0
            _mem4.channel_attributes[number].unknown1 = 0
            _mem4.channel_attributes[number].unknown2 = 0
            _mem4.channel_attributes[number].is_free = 1
            _mem4.channel_attributes[number].band = 0x7

        # find band
        band = _find_band(self, mem.freq)

        # mode
        if mem.mode == "NFM":
            _mem.bandwidth = 1
            _mem.enable_am = 0
        elif mem.mode == "FM":
            _mem.bandwidth = 0
            _mem.enable_am = 0
        elif mem.mode == "NAM":
            _mem.bandwidth = 1
            _mem.enable_am = 1
        elif mem.mode == "AM":
            _mem.bandwidth = 0
            _mem.enable_am = 1

        # frequency/offset
        _mem.freq = mem.freq/10
        _mem.offset = mem.offset/10

        if mem.duplex == "off" or mem.duplex == "":
            _mem.offset = 0
            _mem.shift = 0
        elif mem.duplex == '-':
            _mem.shift = FLAGS1_OFFSET_MINUS
        elif mem.duplex == '+':
            _mem.shift = FLAGS1_OFFSET_PLUS

        # set band
        if number < 200:
            _mem4.channel_attributes[number].is_free = 0
            _mem4.channel_attributes[number].band = band

        # channels >200 are the 14 VFO chanells and don't have names
        if number < 200:
            _mem2 = self._memobj.channelname[number]
            tag = mem.name.ljust(10) + "\x00"*6
            _mem2.name = tag  # Store the alpha tag

        # tone data
        self._set_tone(mem, _mem)

        # step
        _mem.step = STEPS.index(mem.tuning_step)

        # tx power
        if str(mem.power) == str(UVK5_POWER_LEVELS[2]):
            _mem.txpower = POWER_HIGH
        elif str(mem.power) == str(UVK5_POWER_LEVELS[1]):
            _mem.txpower = POWER_MEDIUM
        else:
            _mem.txpower = POWER_LOW

        for setting in mem.extra:
            sname = setting.get_name()
            svalue = setting.value.get_value()

            if sname == "bclo":
                _mem.bclo = svalue and 1 or 0

            if sname == "pttid":
                _mem.dtmf_pttid = PTTID_LIST.index(svalue)

            if sname == "frev":
                _mem.freq_reverse = svalue and 1 or 0

            if sname == "dtmfdecode":
                _mem.dtmf_decode = svalue and 1 or 0

            if sname == "scrambler":
                _mem.scrambler = (
                    _mem.scrambler & 0xf0) | SCRAMBLER_LIST.index(svalue)

            if number < 200 and sname == "scanlists":
                if svalue == "1":
                    _mem4.channel_attributes[number].is_scanlist1 = 1
                    _mem4.channel_attributes[number].is_scanlist2 = 0
                elif svalue == "2":
                    _mem4.channel_attributes[number].is_scanlist1 = 0
                    _mem4.channel_attributes[number].is_scanlist2 = 1
                elif svalue == "1+2":
                    _mem4.channel_attributes[number].is_scanlist1 = 1
                    _mem4.channel_attributes[number].is_scanlist2 = 1
                else:
                    _mem4.channel_attributes[number].is_scanlist1 = 0
                    _mem4.channel_attributes[number].is_scanlist2 = 0

        return mem


@directory.register
class UVK5Radio_nolimit(UVK5Radio):
    VENDOR = "Quansheng"
    MODEL = "UV-K5 (modified firmware)"
    VARIANT = "nolimits"
    FIRMWARE_NOLIMITS = True

    def get_features(self):
        rf = UVK5Radio.get_features(self)
        # This is what the BK4819 chip supports
        rf.valid_bands = [(18000000,  620000000),
                          (840000000, 1300000000)
                          ]
        return rf
