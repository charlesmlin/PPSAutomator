# PPSAutomator
Features
1. Gaurantees that consecutive transaction amount is not unique
1. Guarantees transaction amount falls within 1.00 and 1.04, except the last two transactions to gaurantee completeness

Current assumptions / restrictions:
1. Chrome is installed ([Download here](https://www.google.com/chrome) if not)
1. Chrome stable build or beta build is used
1. Bill is already registered ![Registered_Bill](/images/Registered_Bill.png)
1. There is only one registered bill per merchant code

Note:
1. If during execution of assemble.sh, tensorflow library pops up, please follow the solution in [pyinstaller github](https://github.com/pyinstaller/pyinstaller/issues/4400#issuecomment-550905592)
   1. copy site-packages/tensorflow_core folder into <project folder>, and RENAME it to tensorflow
   1. open <project folder>/tensorflow/lite/python/lite.py and comment out line 31
      ```
      from tensorflow.lite.experimental.microfrontend.python.ops import audio_microfrontend_op
      ```
   1. execute assemble.sh