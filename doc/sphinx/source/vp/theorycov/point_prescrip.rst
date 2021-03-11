.. The line below allows you to break to a new line by adding |br| at the end of the line
.. |br| raw:: html 

.. _prescrips:

Point prescriptions for theory covariance matrices
==================================================

The equations below display the different point prescriptions, as they
appear in ``validphys2``.

3 points
--------
.. note:: 

	``theoryids``: 163, 180, 173	|br|
	``point_prescription: '3 point'``
	
.. math:: s_{11} = \frac{1}{2}\bigg\{ \Delta_1(+,+)^2 + \Delta_1(-,-)^2 \bigg\}

.. math:: s_{12} = \frac{1}{4}\bigg\{\bigg(\Delta_1(+,+) + \Delta_1(-,-) \bigg) \bigg(\Delta_2(+,+) + \Delta_2(-,-) \bigg) \bigg\}


5 points
---------
.. note::

	``theoryids``: 163, 177, 176, 179, 174 |br|
	``point_prescription: '5 point'``
.. math:: s_{11} = \frac{1}{2}\bigg\{ \Delta_1(+,0)^2 + \Delta_1(-,0)^2 + \Delta_1(0,+)^2 + \Delta_1(0,-)^2 \bigg\}

.. math::

   \begin{split}
       s_{12} = \frac{1}{2}\bigg\{ &\Delta_1(+,0)\Delta_2(+,0) + \Delta_1(-,0)\Delta_2(-,0) \bigg\} \\
               + \frac{1}{4}\bigg\{ &\bigg(\Delta_1(0,+) + \Delta_1(0,-) \bigg)\bigg(\Delta_2(0,+) + \Delta_2(0,-)\bigg)\bigg\}
   \end{split}

:math:`\mathbf{\overline{5}}` points
------------------------------------
.. note::

	``theoryids:`` 163, 180, 173, 175, 178 |br|
	``point_prescription: '5bar point'``
	
.. math:: s_{11} = \frac{1}{2}\bigg\{ \Delta_1(+,+)^2 + \Delta_1(-,-)^2 + \Delta_1(+,-)^2 + \Delta_1(-,+)^2 \bigg\}

.. math::

   \begin{split}
       s_{12} = \frac{1}{4}\bigg\{ &\bigg(\Delta_1(+,+) + \Delta_1(+,-)\bigg) \bigg(\Delta_2(+,+) + \Delta_2(+,-) \bigg) \\
       + &\bigg(\Delta_1(-,+) + \Delta_1(-,-)\bigg) \bigg(\Delta_2(-,+) + \Delta_2(-,-) \bigg) \bigg\}
   \end{split}

7 points - original
-------------------

.. warning::

	**Deprecated prescription!** |br|
	``theoryids:`` 163, 177, 176, 179, 174, 180, 173 |br|
 	Specify in the runcard ``seventheories: original`` |br|
	``point_prescription: '7 point'``
	
.. math::

     \begin{split}
         s_{11} = \frac{1}{3}\bigg\{ &\Delta_1(+,0)^2 + \Delta_1(-,0)^2 + \Delta_1(0,+)^2 + \Delta_1(0,-)^2  \\                                 + &\Delta_1(+,+)^2 + \Delta_1(-,-)^2 \bigg\}
     \end{split}

.. math::

   \begin{split}
       s_{12} = \frac{1}{6}\bigg\{ &\bigg(\Delta_1(+,0) + \Delta_1(+,+) \bigg) \bigg(\Delta_2(+,0) + \Delta_2(+,+) \bigg) \\
               + &\bigg(\Delta_1(-,0)+\Delta_1(-,-)\bigg) \bigg(\Delta_2(-,0) + \Delta_2(-,-) \bigg) \\
               + &\bigg(\Delta_1(0,+)+\Delta_1(0,-)\bigg)\bigg(\Delta_2(0,+) + \Delta_2(0,-) \bigg)\bigg\}
   \end{split}

7 points - Gavin (default)
--------------------------
.. note::

	``theoryids:`` 163, 177, 176, 179, 174, 180, 173 |br|
	``point_prescription: '7 point'``

.. math::

   \begin{split}
       s_{11} = \frac{1}{3}\bigg\{ &\Delta_1(+,0)^2 + \Delta_1(-,0)^2 + \Delta_1(0,+)^2 + \Delta_1(0,-)^2  \\                                 + &\Delta_1(+,+)^2 + \Delta_1(-,-)^2 \bigg\}
   \end{split}

.. math::

   \begin{split}
       s_{12} = \frac{1}{6}\bigg\{ &2\bigg(\Delta_1(+,0)\Delta_2(+,0) + \Delta_1(-,0)\Delta_2(-,0) \bigg) \\
               + &\bigg(\Delta_1(0,+)+\Delta_1(0,-)\bigg) \bigg(\Delta_2(0,+) + \Delta_2(0,-) \bigg) \\
               + &\bigg(\Delta_1(+,+)+\Delta_1(-,-)\bigg)\bigg(\Delta_2(+,+) + \Delta_2(-,-) \bigg)\bigg\}
   \end{split}

.. _points-2:

9 points
--------

.. note::

	``theoryids:`` 163, 177, 176, 179, 174, 180, 173, 175, 178 |br|
	``point_prescription: '9 point'``

.. math::

   \begin{split}
       s_{11} = \frac{1}{4}\bigg\{ &\Delta_1(+,0)^2 + \Delta_1(-,0)^2
                               + \Delta_1(0,+)^2 + \Delta_1(0,-)^2 \\
                               + &\Delta_1(+,+)^2 + \Delta_1(+,-)^2 
                               + \Delta_1(-,+)^2 + \Delta_1(-,-)^2 \bigg\}
   \end{split}

.. math::

   \begin{split}
       s_{12} = \frac{1}{12}\bigg\{&\bigg(\Delta_1(+,0)+\Delta_1(+,+) + \Delta_1(+,-)\bigg) \bigg(\Delta_2(+,0) + \Delta_2(+,+) + \Delta_2(+,-) \bigg) \\
               + &\bigg(\Delta_1(-,0) + \Delta_1(-,+) + \Delta_1(-,-)\bigg)\bigg(\Delta_2(-,0) + \Delta_2(-,+) + \Delta_2(-,-) \bigg) \bigg\}\\
               + \frac{1}{8}&\bigg(\Delta_1(0,+)+ \Delta_1(0,-)\bigg)\bigg(\Delta_2(0,+) + \Delta_2(0,-) \bigg)
   \end{split}

