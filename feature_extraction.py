import sys
import cv2
import numpy
import time
from PIL import Image


from phasepack.phasesym import phasesym
from phasepack.phasecongmono import phasecongmono

def main():
    # testImage()
    imagePath = sys.argv[1]
    img = cv2.imread(imagePath)
    findBalance(img)
    findSymmetry(img)
    # findWhiteSpace(img)

# def testImage():
#     arr = numpy.zeros((50, 50)) * 255

#     print(arr)

#     img = Image.fromarray(arr.astype(numpy.uint8), 'L')
#     img.save("/Users/tjia/Dropbox (GaTech)/Gatech/Spring_2021/LMC6650/Artifacts/phaseSym/test.jpg")

def findSymmetry(img, dheight=50, dwidth=50):

    res = cv2.resize(img, dsize=(dheight,dwidth))
    phaseSym, orientation, totalEnergy, T = phasesym(res, norient=4, polarity=-1)

    vertical_phaseSym = numpy.absolute(numpy.multiply(phaseSym, numpy.cos(orientation / 180 * numpy.pi)))
    horizontal_phaseSym = numpy.multiply(phaseSym, numpy.sin(orientation / 180 * numpy.pi))
    upward_diagnal_phaseSym = numpy.absolute(numpy.multiply(phaseSym, numpy.sin((orientation - 45)/ 180 * numpy.pi)))
    downward_diagnal_phaseSym = numpy.absolute(numpy.multiply(phaseSym, numpy.sin((orientation + 45)/ 180 * numpy.pi)))


    img = Image.fromarray((vertical_phaseSym * 255).astype(numpy.uint8), 'L')
    img.save("/Users/tjia/Dropbox (GaTech)/Gatech/Spring_2021/LMC6650/Artifacts/phaseSym/" + str(time.time()) + ".png")

    img = Image.fromarray((horizontal_phaseSym * 255).astype(numpy.uint8), 'L')
    img.save("/Users/tjia/Dropbox (GaTech)/Gatech/Spring_2021/LMC6650/Artifacts/phaseSym/" + str(time.time()) + ".png")

    img = Image.fromarray((upward_diagnal_phaseSym * 255).astype(numpy.uint8), 'L')
    img.save("/Users/tjia/Dropbox (GaTech)/Gatech/Spring_2021/LMC6650/Artifacts/phaseSym/" + str(time.time()) + ".png")

    img = Image.fromarray((downward_diagnal_phaseSym * 255).astype(numpy.uint8), 'L')
    img.save("/Users/tjia/Dropbox (GaTech)/Gatech/Spring_2021/LMC6650/Artifacts/phaseSym/" + str(time.time()) + ".png")

    # numpy.savetxt('orientation.csv', numpy.cos(orientation / 180 * numpy.pi), delimiter=",", fmt='%1.3f')

    vertical_symmetry_score = numpy.sum(vertical_phaseSym) / numpy.count_nonzero(phaseSym)
    print("vertical symmetry score for image is " + str(vertical_symmetry_score))
    horizontal_symmetry_score = numpy.sum(horizontal_phaseSym) / numpy.count_nonzero(phaseSym)
    print("horizontal symmetry score for image is " + str(horizontal_symmetry_score))
    down_diagnal_symmetry_score = numpy.sum(downward_diagnal_phaseSym) / numpy.count_nonzero(phaseSym)
    print("diagnal symmetry score for image is " + str(down_diagnal_symmetry_score))
    up_diagnal_symmetry_score = numpy.sum(upward_diagnal_phaseSym) / numpy.count_nonzero(phaseSym)
    print("opposite diagnal symmetry score for image is " + str(up_diagnal_symmetry_score))
    print("\n")
    return vertical_symmetry_score, horizontal_symmetry_score, up_diagnal_symmetry_score, down_diagnal_symmetry_score

def findBalance(img, dheight=50, dwidth=50):

    res = cv2.resize(img, dsize=(dheight,dwidth))

    congruency = (255 - cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)) / 255

    img = Image.fromarray((congruency).astype(numpy.uint8), 'L')
    img.save("/Users/tjia/Dropbox (GaTech)/Gatech/Spring_2021/LMC6650/Artifacts/cong/" + str(time.time()) + ".png")


    total_points = numpy.count_nonzero(congruency)

    # vertical_balance_score = (numpy.sum(congruency[0:(dheight//2)]) - numpy.sum(congruency[(dheight//2):dheight])) / total_points
    # print("vertical balance score for image is " + str(vertical_balance_score))
    # horizontal_balance_score = (numpy.sum(congruency[:, 0:(dwidth//2)]) - numpy.sum(congruency[:, (dwidth//2):dwidth])) / total_points
    # print("horizontal balance score for image is " + str(horizontal_balance_score))
    # diagnal_balance_score = (numpy.triu(congruency).sum() - numpy.tril(congruency).sum()) / total_points
    # print("diagnal balance score for image is " + str(diagnal_balance_score))

    # opposite_congruency = numpy.fliplr(congruency)
    # opposite_diagnal_balance_score = (numpy.triu(opposite_congruency).sum() - numpy.tril(opposite_congruency).sum()) / total_points
    # print("opposite diagnal balance score for image is " + str(opposite_diagnal_balance_score))

    vertical_balance_score = (numpy.count_nonzero(congruency[0:(dheight//2)]) - numpy.count_nonzero(congruency[(dheight//2):dheight])) / total_points
    print("vertical balance score for image is " + str(vertical_balance_score))
    horizontal_balance_score = (numpy.count_nonzero(congruency[:, 0:(dwidth//2)]) - numpy.count_nonzero(congruency[:, (dwidth//2):dwidth])) / total_points
    print("horizontal balance score for image is " + str(horizontal_balance_score))
    diagnal_balance_score = (numpy.count_nonzero(numpy.triu(congruency)) - numpy.count_nonzero(numpy.tril(congruency))) / total_points
    print("diagnal balance score for image is " + str(diagnal_balance_score))

    opposite_congruency = numpy.fliplr(congruency)
    opposite_diagnal_balance_score = (numpy.count_nonzero(numpy.triu(opposite_congruency)) - numpy.count_nonzero(numpy.tril(opposite_congruency))) / total_points
    print("opposite diagnal balance score for image is " + str(opposite_diagnal_balance_score))
    print("\n")

    return vertical_balance_score, horizontal_balance_score, diagnal_balance_score, opposite_diagnal_balance_score

def findWhiteSpace(img, dheight=50, dwidth=50):

    res = cv2.resize(img, dsize=(dheight,dwidth))
    all_phaseSym, orientation, totalEnergy, T = phasesym(res, norient=4, polarity=0)
    negative_phaseSym, orientation, totalEnergy, T = phasesym(res, norient=4, polarity=-1)


    # vertical_phaseSym = numpy.absolute(numpy.multiply(phaseSym, numpy.cos(orientation / 180 * numpy.pi)))
    # horizontal_phaseSym = numpy.multiply(phaseSym, numpy.sin(orientation / 180 * numpy.pi))
    # upward_diagnal_phaseSym = numpy.absolute(numpy.multiply(phaseSym, numpy.sin((orientation - 45)/ 180 * numpy.pi)))
    # downward_diagnal_phaseSym = numpy.absolute(numpy.multiply(phaseSym, numpy.sin((orientation + 45)/ 180 * numpy.pi)))


    img = Image.fromarray(((all_phaseSym - negative_phaseSym) * 255).astype(numpy.uint8), 'L')
    img.save("/Users/tjia/Dropbox (GaTech)/Gatech/Spring_2021/LMC6650/Artifacts/phaseSym/" + str(time.time()) + ".png")

    # numpy.savetxt('orientation.csv', numpy.cos(orientation / 180 * numpy.pi), delimiter=",", fmt='%1.3f')

    symmetry_score = numpy.sum(all_phaseSym - negative_phaseSym) / (dheight * dwidth)
    print("symmetry score for image is " + str(symmetry_score))

    return symmetry_score



if __name__ == '__main__':
    main()