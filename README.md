# studio

<p align="center">
    <a>
       <img src="https://img.shields.io/badge/-Python-F9DC3E.svg?logo=python&style=flat">
    </a>
    <a>
      <img src="https://img.shields.io/badge/-TypeScript-007ACC.svg?logo=typescript&style=flat&logoColor=white">
    </a>
    <a href="https://github.com/arayabrain/MRIAnalysisStudioforMouse">
      <img alt="" src="https://img.shields.io/github/repo-size/arayabrain/MRIAnalysisStudioforMouse">
    </a>
    <a href="https://github.com/arayabrain/MRIAnalysisStudioforMouse">
      <img alt="" src="https://img.shields.io/github/stars/arayabrain/MRIAnalysisStudioforMouse?style=social">
    </a>
    <a href="https://github.com/arayabrain/MRIAnalysisStudioforMouse">
      <img alt="" src="https://img.shields.io/github/forks/arayabrain/MRIAnalysisStudioforMouse?style=social">
    </a>
</p>

studio(Optical Neuroimage Studio) is a GUI based workflow pipeline tools for processing two-photon calcium imaging data.

studio helps researchers try multiple data analysis methods, visualize the results, and construct the data analysis pipelines easily and quickly on GUI. studio's data-saving format follows NWB standards.

studio also supports reproducibility of scientific research, standardization of analysis protocols, and developments of novel analysis tools as plug-in.

## Key Features
### :beginner: Easy-To-Create Workflow
- **zero-knowledge of coding**: studio allows you to create analysis pipelines easily on the GUI.

### :zap: Visualizing analysis results
- **quick visualization**: studio supports you visualize the analysis results by plotly.

### :rocket: Managing Workflows
- **recording and reproducing**: studio records and reproduces the workflow pipelines easily.


## Installation

### Prepare configuration files

#### Prepare .env

- Copy `.env.example` to `.env` and replace `SECRET_KEY` in `.env` with your SECRET_KEY.
  - To create random SECRET_KEY:
    ```
    openssl rand -hex 32
    ```

#### Prepare firebase configs

This application uses firebase.

- Copy `firebase_config.example.json` to `firebase_config.json` and replace content of `firebase_config.json` with your Firebase config.
- Copy `firebase_private.example.json` to `firebase_private.json` and replace content of `firebase_private.json` with your Firebase private key.

#### Prepare firebase configs

### Running Application

**Docker required:** Please install docker in advance.

- On Linux(Ubuntu) or macOS or Windows:
  - Run the file to set up and start the app:

    ```
    docker compose up
    ```

Open browser. http://localhost:8000

## Using GUI
### Workflow
- studio allows you to make your analysis pipelines by graph style using nodes and edges on GUI. Parameters for each analysis are easily changeable.


### Visualize
- studio allows you to visualize the analysis results with one click by plotly. It supports a variety of plotting styles.

### Record
- studio supports you in recording and reproducing workflow pipelines in an organized manner. 



## Contributors
### Proposers
[Sho Yagishita](https://sites.google.com/view/yagishita-group)

### Developers
[Keita Matsumoto](https://github.com/emuemuJP), [Nobuo Kawada](https://github.com/itutu-tienday), [Rei Hashimoto](https://github.com/ReiHashimoto), [Naoki Takada](https://github.com/takada-naoki-github), [Atsuo Matsueda](https://github.com/Matsueda-Atsuo)

## References
This product is based on [OptiNiSt](https://github.com/oist/optinist), proposed by [OIST Neural Computation Unit](https://groups.oist.jp/ncu)

<!-- ## Citing the Project
To cite this repository in publications:
```
@misc{studio,
  author = {name},
  title = {title},
  year = {2022},
  publisher = {},
  journal = {},
  howpublished = {},
}
``` -->
