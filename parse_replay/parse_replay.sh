python3 extract_actions.py --hq_replay_set $1 --n_instance $2 &&
python3 sample_actions.py --hq_replay_set $1 &&
python3 parse_replay.py --hq_replay_set $1 --n_instance $2 &&
python3 replay2global_features.py --hq_replay_set $1