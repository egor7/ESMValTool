"""Gradient Boosting Regression model."""

import logging
import os

import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble.partial_dependence import plot_partial_dependence

from esmvaltool.diag_scripts.mlr.models import MLRModel

logger = logging.getLogger(os.path.basename(__file__))


@MLRModel.register_mlr_model('gbr')
class GBRModel(MLRModel):
    """Gradient Boosting Regression model.

    Note
    ----
    See :mod:`esmvaltool.diag_scripts.mlr.models`.

    """

    _CLF_TYPE = GradientBoostingRegressor

    def __init__(self, cfg, root_dir=None, **metadata):
        """Initialize child class members."""
        super().__init__(cfg, root_dir=root_dir, **metadata)

    def plot_feature_importance(self, filename=None):
        """Plot feature importance.

        Parameters
        ----------
        filename : str, optional (default: 'feature_importance')
            Name of the plot file.

        """
        if not self._is_ready_for_plotting():
            return
        if filename is None:
            filename = 'feature_importance'
        (_, axes) = plt.subplots()

        # Plot
        feature_importance = self._clf.feature_importances_
        sorted_idx = np.argsort(feature_importance)
        pos = np.arange(sorted_idx.shape[0]) + 0.5
        axes.barh(pos, feature_importance[sorted_idx], align='center')
        axes.set_title('Variable Importance ({} Model)'.format(
            type(self._clf).__name__))
        axes.set_xlabel('Relative Importance')
        axes.set_yticks(pos)
        axes.set_yticklabels(np.array(self.classes['features'])[sorted_idx])
        new_filename = filename + '.' + self._cfg['output_file_type']
        new_path = os.path.join(self._cfg['mlr_plot_dir'], new_filename)
        plt.savefig(new_path, orientation='landscape', bbox_inches='tight')
        logger.info("Wrote %s", new_path)
        axes.clear()
        plt.close()

    def plot_partial_dependences(self, filename=None):
        """Plot partial dependences for every feature.

        Parameters
        ----------
        filename : str, optional (default: 'partial_dependece_of_{feature}')
            Name of the plot file.

        """
        if not self._is_ready_for_plotting():
            return
        if filename is None:
            filename = 'partial_dependece_of_{feature}'

        # Plot for every feature
        for (idx, feature_name) in enumerate(self.classes['features']):
            (_, [axes]) = plot_partial_dependence(self._clf,
                                                  self._data['x_train'], [idx])
            x_label_norm = ('' if self._data['x_norm'][idx] == 1.0 else
                            '{:.2E} '.format(self._data['x_norm'][idx]))
            y_label_norm = ('' if self._data['y_norm'] == 1.0 else
                            '{:.2E} '.format(self._data['y_norm']))
            axes.set_title('Partial dependence ({} Model)'.format(
                type(self._clf).__name__))
            axes.set_xlabel('{} / {}{}'.format(
                feature_name, x_label_norm,
                self.classes['features_units'][idx]))
            axes.set_ylabel('{} / {}{}'.format(self.classes['label'],
                                               y_label_norm,
                                               self.classes['label_units']))
            new_filename = (filename.format(feature=feature_name) + '.' +
                            self._cfg['output_file_type'])
            new_path = os.path.join(self._cfg['mlr_plot_dir'], new_filename)
            plt.savefig(new_path, orientation='landscape', bbox_inches='tight')
            logger.info("Wrote %s", new_path)
            plt.close()

    def plot_prediction_error(self, filename=None):
        """Plot prediction error for training and (if possible) test data.

        Parameters
        ----------
        filename : str, optional (default: 'prediction_error')
            Name of the plot file.

        """
        if not self._is_ready_for_plotting():
            return
        if filename is None:
            filename = 'prediction_error'
        (_, axes) = plt.subplots()

        # Plot train score
        axes.plot(
            np.arange(len(self._clf.train_score_)) + 1,
            self._clf.train_score_,
            'b-',
            label='Training Set Deviance')

        # Plot test score if possible
        if 'x_test' in self._data:
            test_score = np.zeros((len(self._clf.train_score_), ),
                                  dtype=np.float64)
            for (idx, y_pred) in enumerate(
                    self._clf.staged_predict(self._data['x_test'])):
                test_score[idx] = self._clf.loss_(self._data['y_test'], y_pred)
            axes.plot(
                np.arange(len(test_score)) + 1,
                test_score,
                'r-',
                label='Test Set Deviance')
        axes.legend(loc='upper right')
        axes.set_title('Deviance ({} Model)'.format(type(self._clf).__name__))
        axes.set_xlabel('Boosting Iterations')
        axes.set_ylabel('Deviance')
        new_filename = filename + '.' + self._cfg['output_file_type']
        new_path = os.path.join(self._cfg['mlr_plot_dir'], new_filename)
        plt.savefig(new_path, orientation='landscape', bbox_inches='tight')
        logger.info("Wrote %s", new_path)
        axes.clear()
        plt.close()