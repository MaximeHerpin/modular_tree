call conda activate blender_dev
cd ./m_tree
python setup.py develop

COPY "./m_tree.cp37-win_amd64.pyd" "../m_tree.cp37-win_amd64.pyd"

PAUSE


