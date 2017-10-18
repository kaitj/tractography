""" fiber.py

Module containing classes and functions related to processing fiber
information.

"""

import numpy as np
import vtk
from collections import defaultdict

def tree():
    """
    Creates tree to store quantitative information.

    INPUT:
        none

    OUTPUT:
        none
    """

    return defaultdict(tree)

def convertFromTuple(fiberTuple):
    """
    Converts fiber data in form of type tuple (from extraction) to fiberTree.
    Output is of class FiberTree

    INPUT:
        fiberTuple - tuple containing fiber information to be converted

    OUTPUT:
        fiberTree - fiber information converted to a tree
    """

    fiberTree = FiberTree()

    fiberTree.no_of_fibers = len(fiberTuple[0])
    fiberTree.pts_per_fiber = len(fiberTuple[0][0])

    for fidx in range(fiberTree.no_of_fibers):
        for pidx in range(fiberTree.pts_per_fiber):
                fiberTree.fiberTree[fidx][pidx]['x'] = fiberTuple[0][fidx][pidx]
                fiberTree.fiberTree[fidx][pidx]['y'] = fiberTuple[1][fidx][pidx]
                fiberTree.fiberTree[fidx][pidx]['z'] = fiberTuple[2][fidx][pidx]

    return fiberTree

class FiberTree:
    """
    Data pertaining to a group of fibers.
    Value returned is of class FiberTree
    """

    def __init__(self):
        self.fiberTree = tree()

        # Info related to fibers
        self.no_of_fibers = None
        self.pts_per_fiber = None

    def _calc_fiber_indices(self, fiberLength, pts_per_fiber):
        """ *INTERNAL FUNCTION*
        Determine indices to traverse data along a fiber.

        Indices include both end points of the fiber plus evenly spaced points
        along the line. Module determines which indices are wanted based on
        fiber length and desired number of points along the length.

        INPUT:
            fiberLength - Number of points along a fiber
            pts_per_length - Number of desired points along fiber

        OUTPUT:
            idxList - Corresponding new indices to traverse along fiber
        """

        # Step length between points along fiber
        stepLength = (fiberLength - 1.0) / (pts_per_fiber - 1.0)

        # Output indices along fiber
        idxList = []
        for idx in range(0, pts_per_fiber):
            idxList.append(idx * stepLength)

        return idxList

    def getFiber(self, fiberIdx):
        """
        Extract a single fiber from the group with corresponding data.
        Value returned is of class Fiber.

        INPUT:
            fiberIdx - Index of fiber to be extracted

        OUTPUT
            fiber - Single fiber of class Fiber
        """

        # Fiber data
        fiber_x = np.zeros(self.pts_per_fiber)
        fiber_y = np.zeros(self.pts_per_fiber)
        fiber_z = np.zeros(self.pts_per_fiber)

        for pidx in range(0, self.pts_per_fiber):
            fiber_x[pidx] = float(self.fiberTree[fiberIdx][pidx]['x'])
            fiber_y[pidx] = float(self.fiberTree[fiberIdx][pidx]['y'])
            fiber_z[pidx] = float(self.fiberTree[fiberIdx][pidx]['z'])

        return fiber_x, fiber_y, fiber_z

    def getFibers(self, fidxes):
        """
        Extracts a subset of fibers corresponding to inputted indices.
        Returned fibers are of class fiberArray.

        INPUT:
            fidxes - Indices of subset of fibers to be extracted

        OUTPUT:
            fibers - Subset of fibers of class fiberArray
        """

        fiberArray_x = np.zeros((len(fidxes), self.pts_per_fiber))
        fiberArray_y = np.zeros((len(fidxes), self.pts_per_fiber))
        fiberArray_z = np.zeros((len(fidxes), self.pts_per_fiber))

        # Fiber data
        idx = 0
        for fidx in fidxes:
            for pidx in range(0, self.pts_per_fiber):
                fiberArray_x[idx][pidx] = float(self.fiberTree[fidx][pidx]['x'])
                fiberArray_y[idx][pidx] = float(self.fiberTree[fidx][pidx]['y'])
                fiberArray_z[idx][pidx] = float(self.fiberTree[fidx][pidx]['z'])

            idx += 1

        return fiberArray_x, fiberArray_y, fiberArray_z

    def addClusterInfo(self, clusterLabels, centroids):
        """
        Add and save cluster label to fiber tree storing tractography data.

        INPUT:
            clusterLabels - Array of cluster labels sorted in fiber index order
            centroids - Array of centroids associated with fiber clusters

        OUTPUT:
            none
        """

        uniqueLabels = np.unique(clusterLabels, return_counts=False)

        for label in uniqueLabels:
            for fidx in np.where(clusterLabels == label)[0]:
                self.fiberTree[fidx][str(label)] = label
                self.fiberTree['centroid'][label] = centroids[label]

    def addScalar(self, inputVTK, scalarData, scalarType, pts_per_fiber=20):
        """
        Add scalar information pertaining to tractography. Values are
        stored with a tree format. This function is dynamic and can add new
        quantitative measurements as needed.

        INPUT:
            inputVTK - Tractography polydata to extract corresponding indices
            scalarData - List of scalar values to be stored
            scalarType - Type of quantitative scalar (ie. FA, T1)
            pts_per_fiber - Number of samples to take along fiber

        OUTPUT:
            none
        """
        inputVTK.GetLines().InitTraversal()
        ptIds = vtk.vtkIdList()

        # Loop over all fibers
        for fidx in range(0, self.no_of_fibers):
            inputVTK.GetLines().GetNextCell(ptIds)
            fiberLength = ptIds.GetNumberOfIds()

            # Loop over pts for ea. fiber
            pidx = 0
            for lineIdx in self._calc_fiber_indices(fiberLength, pts_per_fiber):

                # Find point index
                ptidx = ptIds.GetId(int(round(lineIdx)))
                self.fiberTree[fidx][pidx][scalarType] = \
                    scalarData[ptidx]

                pidx += 1

    def getScalar(self, fidx, scalarType):
        """
        Extracts scalar information of a specified scalarType pertaining to
        a single fiber.

        INPUT:
            fidx - Index corresponding to fiber to extract scalar information from
            scalarType - Type of quantitative scalar (ie. FA, T1)

        OUTPUT:
            scalarList - List of scalar values indexed by point
        """

        scalarList = np.zeros(self.pts_per_fiber)

        for pidx in range(0, self.pts_per_fiber):

            scalarList[pidx] = float(self.fiberTree[fidx][pidx][scalarType])

        return scalarList

    def getScalars(self, fidxes, scalarType):
        """
        Extracts scalar information of a specified scalarType pertaining to
        a group of fibers.

        INPUT:
            fidxes - Indices corresponding to fibers to extract scalar information from
            scalarType - Type of quantitative scalar (ie. FA, T1)

        OUTPUT:
            scalarList - List of scalar values indexed by fiber and point
        """

        scalarList = np.zeros((len(fidxes), self.pts_per_fiber))

        idx = 0
        for fidx in fidxes:
            for pidx in range(0, self.pts_per_fiber):
                scalarList[idx][pidx] = float(self.fiberTree[fidx][pidx][str(scalarType)])

            idx += 1

        return scalarList

    def convertFromVTK(self, inputVTK, pts_per_fiber=20, verbose=0):
        """
        Convert input tractography VTK data to array form

        INPUT:
            inputVTK - Tractography polydata
            pts_per_fiber - Number of points to sample along a fiber
            verbose - Verbosity of function; 1 to print messages to user.

        OUTPUT:
            none
        """

        self.no_of_fibers = inputVTK.GetNumberOfLines()
        self.pts_per_fiber = pts_per_fiber

        if verbose == 1:
            print "\n<fibers.py> Converting polydata to array representation."
            print "Fibers:", self.no_of_fibers
            print "Points sampled along fiber:", self.pts_per_fiber

        # Loop over all fibers
        inputVTK.GetLines().InitTraversal()
        ptIds = vtk.vtkIdList()
        inputPts = inputVTK.GetPoints()

        for fidx in range(0, self.no_of_fibers):
            inputVTK.GetLines().GetNextCell(ptIds)
            fiberLength = ptIds.GetNumberOfIds()

            # Loop over pts for ea. fiber
            pidx = 0
            for lineIdx in self._calc_fiber_indices(fiberLength,
                                                    self.pts_per_fiber):

                # Perform NN interpolation
                ptidx = ptIds.GetId(int(round(lineIdx)))
                pt = inputPts.GetPoint(ptidx)

                self.fiberTree[fidx][pidx]['x'] = pt[0]
                self.fiberTree[fidx][pidx]['y'] = pt[1]
                self.fiberTree[fidx][pidx]['z'] = pt[2]

                pidx += 1

    def convertToVTK(self):
        """
        Convert fibers in array form to VTK polydata.

        INPUT:
            none

        OUTPUT:
            outVTK - Tractography polydata in VTK form
        """

        outVTK = vtk.vtkPolyData()
        outPts = vtk.vtkPoints()
        outFibers = vtk.vtkCellArray()

        outFibers.InitTraversal()

        # Get fiber information to convert to VTK form
        for fidx in range(0, self.no_of_fibers):
            ptIds = vtk.vtkIdList()

            for pidx in range(0, self.pts_per_fiber):
                idx = outPts.InsertNextPoint(self.fiberTree[fidx][pidx]['x'],
                                                               self.fiberTree[fidx][pidx]['y'],
                                                               self.fiberTree[fidx][pidx]['z'])
                ptIds.InsertNextId(idx)

            outFibers.InsertNextCell(ptIds)

        # Group data into VTK format
        outVTK.SetLines(outFibers)
        outVTK.SetPoints(outPts)

        return outVTK
