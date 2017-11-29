from distutils.core import setup

setup(
    name='stan',
    version='0.1',
    packages=['stan', 'stan.core', 'stan.parser', 'stan.plotter'],
    url='https://github.com/itsens/stan',
    license='MIT',
    author='Sergey Andreev',
    author_email='sa@itsens.pro',
    description='Stat Analyzer for load testers',
    install_requires=['tqdm',
                      'plotly',
                      'numpy',
                      'pandas']
)
