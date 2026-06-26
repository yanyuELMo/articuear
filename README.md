# silentspeechoe

Research codebase for a master thesis on earable sensor-based cross-domain
silent speech experiments with OpenEarable 2.0 data.

The repository focuses on clean, reproducible PyTorch baselines for sensor
encoder evaluation, template generation, and template-based verification
experiments.

## Scope

- Task: earable sensor-based silent speech experiments
- Sensors: `bone_acc` and `imu`
- Data source: OpenEarable 2.0 CSV streams
- Main inputs: event-windowed sensor tensors from `events.csv`
- Baselines: temporal CNN/TCN models for single-sensor authentication
- Robustness setting: IMU augmentation for processed windows

## Experiments

The project is organized into two evaluation blocks.

### 1. Model / Encoder Evaluation

This block evaluates the encoder or model itself. Results are written under
`outputs/runs/<sensor>/...`, for example `outputs/runs/imu/...`.

Only identification metrics are reported here via `metrics_identification`,
for example:

- accuracy
- macro F1
- balanced accuracy
- top-3 accuracy

This block is used to compare encoder quality before template generation.

Result storage for this block:

- encoder performance test results are stored under `outputs/runs/<sensor>/`
- the subfolder name should describe the encoder or method, for example
  `outputs/runs/imu/imu_tcn_first10_identification_semantic_val`

### 2. Template-Based Evaluation

After generating templates, the system is evaluated in a second block with two
subsets.

#### 2.1 Enrolled-User Evaluation

This subset uses the same users that were used to train the encoder and build
the enrolled templates.

It reports:

- identification metrics
- authentication metrics
- attack metrics

Attack is defined as follows:

- for enrolled-user evaluation, the attackers are the remaining unseen users
  that were not used to train the encoder
- one attack trial is one attacker-target pair, where each attacker attacks
  each enrolled target user once
- the attacker uses all of their available event samples as attack attempts,
  including semantic and non-semantic samples and all speaking modes
- attack samples must use the same input representation as the encoder and
  template experiment; for example, a binaural temporal-envelope MLP experiment
  attacks with the corresponding binaural IMU feature files
- if any attempt in the trial crosses the selected target-user authentication
  threshold, the whole trial counts as successful
- `ASR = successful_trials / total_trials`

Authentication reports:

- EER
- FRR at `FAR = 0.1%`
- the actual FAR at the threshold selected for `FAR = 0.1%`

The attack threshold is the target-user threshold selected at the
`FAR = 0.1%` operating point.

#### 2.2 Unseen-User Evaluation

This subset evaluates the remaining unseen users that did not participate in
encoder training.

It reports the same metrics as enrolled-user evaluation:

- identification metrics
- authentication metrics
- attack metrics

The only difference is the attacker pool:

- attackers are sampled from the encoder-training users
- the number of sampled attackers matches the number of unseen users
- for example, if there are 10 unseen users, 10 attackers are sampled from the
  training users

For the current 36/10 split, unseen-user evaluation therefore samples 10
attackers from the 36 encoder-training users.

The template-based evaluation results are also stored under
`outputs/runs/<sensor>/...`, together with the corresponding threshold and
attack summaries.

Result storage for template generation and system evaluation:

- generated templates are stored under `outputs/templates/<sensor>/<method>/`
- the method folder should match the encoder or template method that produced
  the templates, for example `outputs/templates/imu/tcn/`
- within that method folder, keep separate subfolders for enrolled-user
  templates and unseen-user templates
- template-based system evaluation results are stored in the same folder used
  for the encoder performance test, under `outputs/runs/<sensor>/<method>/`
- template result batches should be stored under the corresponding encoder run
  folder as `templates_result_<method_and_model>/`
- inside that result batch folder, keep one result subfolder per template
  folder, using the same name as the template folder; for example:
  `outputs/runs/imu/imu_features_mlp_subjects36_nonsemantic/templates_result_temporal_envelope_mlp_mlp/subjects36_nonsemantic_normal_multicenter_k3/`

## Data Layout

Raw data is expected under:

```text
data/raw/
```

Event metadata is expected at:

```text
data/metadata/events.csv
```

Processed window datasets are stored under:

```text
data/processed/imu/imu_windows/
data/processed/bone_acc/bone_acc_windows/
```

Current clean processed datasets:

```text
data/processed/imu/imu_windows/imu_189
data/processed/bone_acc/bone_acc_windows/bone_acc_1000
```

Each processed dataset contains `.pt` samples plus a `manifest.json`. Sample
tensors use `[channels, time]` layout:

```text
IMU:      [9, T] at 189 Hz
bone_acc: [3, T] at 1000 Hz
```

## Preprocessing

Create clean processed windows from `events.csv`:

```bash
python scripts/preprocess.py \
  --imu-sample-rate 189 \
  --bone-acc-sample-rate 1000 \
  --overwrite
```

### IMU Augmentation

The implementation lives in `src/silentspeechoe/data/imu_augmentation.py` and
is wired into the IMU dataset loaders.

For training-time augmentation of preprocessed IMU windows, use:

```bash
python scripts/train.py train=imu_left_tcn_augmented
```

You can also override the block directly:

```bash
python scripts/train.py \
  train=imu_left_tcn \
  train.augmentation.enabled=true \
  train.augmentation.sample_prob=0.1 \
  train.augmentation.rotation_prob=0.05 \
  train.augmentation.rotation_max_degrees=10.0 \
  train.augmentation.time_warp_prob=0.05 \
  train.augmentation.time_warp_min_scale=0.9 \
  train.augmentation.time_warp_max_scale=1.1 \
  train.augmentation.scaling_prob=0.05 \
  train.augmentation.scaling_min_scale=0.9 \
  train.augmentation.scaling_max_scale=1.1 \
  train.augmentation.gaussian_noise_prob=0.05 \
  train.augmentation.gaussian_noise_min_ratio=0.01 \
  train.augmentation.gaussian_noise_max_ratio=0.03
```

Recommended light settings:

- sample gate: `p=0.1`
- rotation: `p=0.05`, `±5°` to `±10°`
- time warping: `p=0.05`, `0.9` to `1.1`
- scaling: `p=0.05`, `0.9` to `1.1`
- gaussian noise: `p=0.05`, `0.01` to `0.03` times per-channel std

The augmenter keeps the original tensor in `x_original` before any change
is applied, which is useful for debugging or audit checks.

Start with small perturbations first. Too much noise can hurt silent-speech
generalization and may raise FAR.

## Models

The temporal model module provides separate entry points for the two processed
sensor types:

```text
BoneAccTemporalCNN  -> bone_acc windows, default 3 channels
IMUTemporalCNN      -> IMU windows, default 9 channels
BoneRawTCN          -> backward-compatible binaural bone_acc model, 6 channels
```

Hydra model configs include:

```text
configs/model/bone_acc_temporal_cnn.yaml
configs/model/imu_temporal_cnn.yaml
```

## Quick Start

Install development dependencies:

```bash
make install-dev
```

Run checks:

```bash
make check
```

Equivalent manual checks:

```bash
ruff check .
ruff format --check .
pytest
```

## Development Notes

- Keep the codebase simple, PyTorch-first, and research-oriented.
- Do not commit raw data, processed tensors, checkpoints, logs, or secrets.
- Use Hydra YAML configs for experiment settings.
- Keep CI lightweight: lint, format check, and tests only.
- GPU validation should remain optional/manual unless a dedicated GPU workflow
  is explicitly added.

## Repository Layout

```text
configs/              Hydra experiment, data, model, and train configs
scripts/              Preprocessing, feature, training, and evaluation entry points
src/silentspeechoe/   Python package for data, features, models, training, evaluation
tests/                Lightweight unit and scaffold tests
data/                 Local data root, ignored for raw/processed artifacts
.devcontainer/        Dev Container and Docker setup
```
