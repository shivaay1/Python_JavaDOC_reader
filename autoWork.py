'''GAURAMATAJIPITAJISHANKAR'''

import html.parser
import os

class FileHandler():

    def __init__(self, fileName ):
        self.fileName = self.filePathCorrector( fileName )

    def filePathCorrector(self, fileName ):
        return "".join( [ char if char != "/" else "\\" for char in fileName ] )

    def getFileName( self ):
        return self.fileName

    def setFileName( self, FileName ):
        self.__init__( fileName )

    def extendPath( self, path ):
        return self.fileName[:-20] + "\\" + self.filePathCorrector( path )



class HTMLFile( FileHandler ):

    def __init__( self, fileName ):
        super().__init__( fileName )
        self.htmlCopy()
        self.hierarchy = self.getTitle()

    def htmlCopy( self ):

        self.file = []
        with open(self.getFileName(), "r" ) as htmlFile:
            for line in htmlFile:
                self.file.append( line )

    def getFile( self ):
        #html file of the HTMLPage
        return self.file

    def setHierarchy( self, name):
        self.hierarchy = name

    def tagDestroyer( self, content ):

        content = content.strip().partition( ">" )[-1]
        content = content.rpartition( "<" )[0]
        return content

    def getTitle( self ):

        for line in self.file:
            if ("<title>") in line:
                return self.tagDestroyer( line )

        else: return "noTitleAvailable"

    def packages( self ):

        content = []
        for num, line in enumerate( self.file ):
            if '<ul title="Packages">' in line:
                for packages in self.file[num+1:]:
                    if '</ul>' in packages:
                        return content
                    content.append(packages)


    def packagesLink( self ):

        links = []
        content = self.packages()
        for item in content:
            link = self.tagDestroyer( item )
            package = self.tagDestroyer( link )

            links.append( ( package, link.split( '"' )[1] ) )

        return links

    def createPackages( self ):

        packages = self.packagesLink()
        for num, package in enumerate( packages ):
            page = HTMLFile( self.extendPath( package[1] ) )
            page.setHierarchy( package[0] )
            packages[num] = page

        return packages


    def createSubClasses( self ):

        content = []
        for num, line in enumerate( self.file ):
            if '<div class="indexContainer">' in line:
                for packages in self.file[num+1:]:
                    if '</div>' in packages:
                        return content
                    content.append(packages)

    def filterPackages( self ):

        content = self.createSubClasses()

        for num, tag in enumerate(content):
            if  "<h2" in tag:
                del content[num]

        return content

    def getFiles( self ):

        contents = {}
        content = self.filterPackages()
        for num, tag in enumerate(content):
            if '<ul title="' in tag:
                tagName = tag.split( '"' )[1]
                contents.update({tagName: []})
                for obj in content[num+1:]:
                    if "</ul>" in obj:
                        break
                    else:
                        contents[tagName].append(obj)

        return contents

    def transformLink( self, link ):
        return link.split( '"' )[1]

    def transformFiles( self ):

        contents = self.getFiles()

        for key, value in contents.items():
            for num, link in enumerate(value):
                contents[key][num] = self.transformLink( link )

        return contents

    def getFileLinks( self ):

        fileName = self.getFileName()
        contents = self.transformFiles()
        for key, value in contents.items():
            for num, link in enumerate(value):
                newFileName = fileName[:-18] + link
                contents[key][num] = newFileName

        return contents

class Package():

    def __init__( self, path, packageName, packageContent ):
        self.path = path
        self.packageName = packageName
        self.packageContent = packageContent
        self.packages = self.generatePackage()

    def generatePackage( self ):
        packageItems = {"Interfaces" : [],
                        "Classes" : [],
                        "Enums" : [],
                        "Exceptions" : [] }

        for key, value in self.packageContent.items():
            for fileName in value:

                if key == "Interfaces":
                    packageItems["Interfaces"].append(JavaInterface( fileName ))
                elif key == "Classes":
                    packageItems["Classes"].append(JavaClass( fileName ))
                elif key == "Enums":
                    packageItems["Enums"].append(JavaEnum( fileName ))
                elif key == "Exceptions":
                    packageItems["Exceptions"].append(JavaException( fileName ))

        return packageItems

    def getPackagePages( self ):
        return self.packages

    def getClasses( self ):
        return self.packages["Classes"]

    def getInterfaces( self ):
        return self.packages["Interfaces"]

    def getEnums( self ):
        return self.packages["Enums"]

    def getExceptions( self ):
        return self.packages["Exceptions"]

    def getAllName( self ):

        if self.getClasses():
            for jvClass in self.getClasses():
                #print("filename ", jvClass.classNameSpecifier())
                print("class name:  ", jvClass.constructFile(self.packageName), end="\n")
                #print("class fields:  ", jvClass.classFields())
                #print("class constructors:  ", jvClass.classConstructors())
                #print("class methods:  ", jvClass.classMethods())
                pass

        for jvInterface in self.getInterfaces():
            #print("interfaces ", jvInterface.hierarchy, " ", self.path)
            print("class name:  ", jvInterface.constructFile(self.packageName), end="\n")
            pass

        for jvEnum in self.getEnums():
            #print("interfaces ", jvInterface.hierarchy, " ", self.path)
            print("class name:  ", jvEnum.constructFile(self.packageName), end="\n")
            pass

        for jvException in self.getExceptions():
            #print("interfaces ", jvInterface.hierarchy, " ", self.path)
            print("class name:  ", jvException.constructFile(self.packageName), end="\n")
            pass



class JavaClass( HTMLFile ):

    def __init__( self, fileName ):
        super().__init__( fileName )
        self.className = self.getTitle()

    def deleteLinks( self, list ):

        newList = []
        for num, tag in enumerate( list ):
            if "<a href=" in tag:
                index = tag.find("<a")
                for itr, str in enumerate( tag[index:] ):
                    if ">" == str:
                        newTag = tag[itr+index:]
                        #print("new Tag : ", newTag)
                        newList.append( newTag )
                        break
                continue

            newList.append( tag )
        return newList


    def classNameSpecifier( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<span class="typeNameLabel">' in tag:
                classNameSpecifier = tag.split(">")[1].split( "<" )[0] + self.className
            else:
                classNameSpecifier = ""

            if "extends <a" in tag:
                extends = tag.split( "<" )[1].split( ">" )[-1]
                if "Object" not in extends:
                    classNameSpecifier += " extends " + extends

            if "implements <a" in tag:
                implements = tag.split( "<" )[1].split( ">" )[-1]
                classNameSpecifier += " implements " + implements
                break;

        return (classNameSpecifier + "{")

    def classFields( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Field Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ========= CONSTRUCTOR DETAIL ======== -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        #fields = self.deleteLinks( fields )
        classFields = []

        for num, field in enumerate( fields ):
            if "<h4>" in field:
                fieldName = self.tagDestroyer( field )
                fieldSpecifier = fields[num+1]
                specificField = self.deleteLinks( [fieldSpecifier] )[0]
                if specificField.startswith( "<pre>" ):
                    newField = specificField.split( ";" )[-1].split( "</pre>" )[0]
                    newField = "private " + newField + ";"
                    classFields.append( newField )

                elif specificField.startswith( ">" ):

                    if "<a href=" in specificField:
                        delLink = self.deleteLinks([specificField])[0]
                        inSharpParenthesis = delLink.split( "</a>" )[0][1:] + ">"
                        fieldName = delLink.split( ";" )[-1].split( "<" )[0]
                        newField = "private " + specificField.split( "</a>" )[0][1:] + "<" + inSharpParenthesis + fieldName + ";"
                        classFields.append( newField )

                    else:
                        fieldType = specificField.split( "</a>" )[0][1:]
                        fieldName = specificField.split( "</a>" )[1].split( "</pre>" )[0]
                        newField = "private " + fieldType + fieldName + ";"
                        classFields.append( newField )

        return list(dict.fromkeys(classFields))

    def makePrettier( self, element ):

        return element.replace("&nbsp;", " ").replace("</a>", "").replace("<pre>", "").replace("</pre>", "")

    def classConstructors( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Constructor Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ============ METHOD DETAIL ========== -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        newConstructor = []
        for num, tag in enumerate( fields ):
            if "<h4>" in tag:
                constructorName = self.tagDestroyer( tag )
                oneConstructor = []
            if "<pre>" in tag:
                for newTag in fields[num:]:
                    if "</pre>" in newTag:
                        oneConstructor.append( self.makePrettier(newTag.strip()))
                        newConstructor.append(oneConstructor)
                        break
                    else:
                        oneConstructor.append(self.makePrettier(newTag.strip()))

        #print("new Constr before ", newConstructor)

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr ):
                if "<a href=" in nxtConstr:
                    processedConstr = nxtConstr
                    while (processedConstr.find("<a href=") != -1):
                        processedConstr = nxtConstr[:nxtConstr.find("<a href")] + nxtConstr[nxtConstr.find(">")+1:]
                        newConstructor[num][nxtNum] = processedConstr
                        nxtConstr = processedConstr

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr ):
                newConstructor[num][nxtNum] = nxtConstr.replace("&lt;", "<").replace("&gt;", ">")

        finalConsructors = []

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr[:-1] ):
                if "," in nxtConstr:
                    finalConsructors.append(" ".join(constr)+"{}")
                else:
                    finalConsructors.append(nxtConstr+"{}")

        return list(dict.fromkeys(finalConsructors))

    def classMethods( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Method Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ========= END OF CLASS DATA ========= -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        newMethods = []
        for num, tag in enumerate( fields ):
            if "<h4>" in tag:
                #methodName = self.tagDestroyer( tag )
                oneMethod = []
            if "<pre>" in tag:
                for newTag in fields[num:]:
                    if "</pre>" in newTag:
                        oneMethod.append( self.makePrettier(newTag.strip()))
                        newMethods.append(oneMethod)
                        break
                    else:
                        oneMethod.append(self.makePrettier(newTag.strip()))

        #print("newMethod: ", newMethods)

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if "<a href=" in nxtMethod:
                    processedMethod = nxtMethod
                    while (processedMethod.find("<a href=") != -1):
                        processedMethod = nxtMethod[:nxtMethod.find("<a href")] + nxtMethod[nxtMethod.find(">")+1:]
                        newMethods[num][nxtNum] = processedMethod
                        nxtMethod = processedMethod

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                newMethods[num][nxtNum] = nxtMethod.replace("&lt;", "<").replace("&gt;", ">")

        for num, method in enumerate( newMethods ):
            newMethods[num] = list(dict.fromkeys(method))

        #print("newMethod : ", newMethods)

        newMethodsList = []
        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if nxtMethod.startswith("x.deepCopy()"):
                    del newMethods[num][nxtNum]

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if nxtMethod.startswith("x.deepCopy()"):
                    del newMethods[num][nxtNum]

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if "" == nxtMethod:
                    del newMethods[num][nxtNum]

        finalMethods = []
        for method in newMethods:
            if len(method) > 1:
                finalMethods.append(" ".join(method) + "{}")
            else:
                finalMethods.append(method[0] + "{}")

        return list(dict.fromkeys(finalMethods))


    def constructFile( self, packageName ):

        folder = "C:/Users/Lalu/Downloads/2020_OOP_UE_Angabe1/project2"
        pages = [ [self.classNameSpecifier()], self.classFields(), self.classConstructors(), self.classMethods()]


        dir = os.path.join(folder, packageName)

        try:
            os.mkdir(dir)
        except FileExistsError :
            os.chdir(dir)

        filePath = os.path.join(os.getcwd(), self.getTitle()) + ".txt"
        #print("filePath: ", filePath)

        with open(filePath, "w") as file:
            for obj in pages:
                for element in obj:
                    file.write("\n")
                    file.writelines(element)
                    file.write("\n")

            file.write("\n")
            file.write("}")






class JavaEnum( HTMLFile ):

    def __init__( self, fileName ):
        super().__init__( fileName )
        self.className = self.getTitle()

    def deleteLinks( self, list ):

        newList = []
        for num, tag in enumerate( list ):
            if "<a href=" in tag:
                index = tag.find("<a")
                for itr, str in enumerate( tag[index:] ):
                    if ">" == str:
                        newTag = tag[itr+index:]
                        #print("new Tag : ", newTag)
                        newList.append( newTag )
                        break
                continue

            newList.append( tag )
        return newList


    def classNameSpecifier( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<span class="typeNameLabel">' in tag:
                classNameSpecifier = tag.split(">")[1].split( "<" )[0] + self.className

            if "extends <a" in tag:
                extends = tag.split( "<" )[1].split( ">" )[-1]
                if "Object" not in extends:
                    classNameSpecifier += " extends " + extends

            if "implements <a" in tag:
                implements = tag.split( "<" )[1].split( ">" )[-1]
                classNameSpecifier += " implements " + implements
                break;

        return (classNameSpecifier + "{")

    def classFields( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Field Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ========= CONSTRUCTOR DETAIL ======== -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        #fields = self.deleteLinks( fields )
        classFields = []

        for num, field in enumerate( fields ):
            if "<h4>" in field:
                fieldName = self.tagDestroyer( field )
                fieldSpecifier = fields[num+1]
                specificField = self.deleteLinks( [fieldSpecifier] )[0]
                if specificField.startswith( "<pre>" ):
                    newField = specificField.split( ";" )[-1].split( "</pre>" )[0]
                    newField = "private " + newField + ";"
                    classFields.append( newField )

                elif specificField.startswith( ">" ):

                    if "<a href=" in specificField:
                        delLink = self.deleteLinks([specificField])[0]
                        inSharpParenthesis = delLink.split( "</a>" )[0][1:] + ">"
                        fieldName = delLink.split( ";" )[-1].split( "<" )[0]
                        newField = "private " + specificField.split( "</a>" )[0][1:] + "<" + inSharpParenthesis + fieldName + ";"
                        classFields.append( newField )

                    else:
                        fieldType = specificField.split( "</a>" )[0][1:]
                        fieldName = specificField.split( "</a>" )[1].split( "</pre>" )[0]
                        newField = "private " + fieldType + fieldName + ";"
                        classFields.append( newField )

        return list(dict.fromkeys(classFields))

    def makePrettier( self, element ):

        return element.replace("&nbsp;", " ").replace("</a>", "").replace("<pre>", "").replace("</pre>", "")

    def classConstructors( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Constructor Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ============ METHOD DETAIL ========== -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        newConstructor = []
        for num, tag in enumerate( fields ):
            if "<h4>" in tag:
                constructorName = self.tagDestroyer( tag )
                oneConstructor = []
            if "<pre>" in tag:
                for newTag in fields[num:]:
                    if "</pre>" in newTag:
                        oneConstructor.append( self.makePrettier(newTag.strip()))
                        newConstructor.append(oneConstructor)
                        break
                    else:
                        oneConstructor.append(self.makePrettier(newTag.strip()))

        #print("new Constr before ", newConstructor)

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr ):
                if "<a href=" in nxtConstr:
                    processedConstr = nxtConstr
                    while (processedConstr.find("<a href=") != -1):
                        processedConstr = nxtConstr[:nxtConstr.find("<a href")] + nxtConstr[nxtConstr.find(">")+1:]
                        newConstructor[num][nxtNum] = processedConstr
                        nxtConstr = processedConstr

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr ):
                newConstructor[num][nxtNum] = nxtConstr.replace("&lt;", "<").replace("&gt;", ">")

        finalConsructors = []

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr[:-1] ):
                if "," in nxtConstr:
                    finalConsructors.append(" ".join(constr)+"{}")
                else:
                    finalConsructors.append(nxtConstr+"{}")

        return list(dict.fromkeys(finalConsructors))

    def classMethods( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Method Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ========= END OF CLASS DATA ========= -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        newMethods = []
        for num, tag in enumerate( fields ):
            if "<h4>" in tag:
                #methodName = self.tagDestroyer( tag )
                oneMethod = []
            if "<pre>" in tag:
                for newTag in fields[num:]:
                    if "</pre>" in newTag:
                        oneMethod.append( self.makePrettier(newTag.strip()))
                        newMethods.append(oneMethod)
                        break
                    else:
                        oneMethod.append(self.makePrettier(newTag.strip()))

        #print("newMethod: ", newMethods)

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if "<a href=" in nxtMethod:
                    processedMethod = nxtMethod
                    while (processedMethod.find("<a href=") != -1):
                        processedMethod = nxtMethod[:nxtMethod.find("<a href")] + nxtMethod[nxtMethod.find(">")+1:]
                        newMethods[num][nxtNum] = processedMethod
                        nxtMethod = processedMethod

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                newMethods[num][nxtNum] = nxtMethod.replace("&lt;", "<").replace("&gt;", ">")

        for num, method in enumerate( newMethods ):
            newMethods[num] = list(dict.fromkeys(method))

        #print("newMethod : ", newMethods)

        newMethodsList = []
        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if nxtMethod.startswith("x.deepCopy()"):
                    del newMethods[num][nxtNum]

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if nxtMethod.startswith("x.deepCopy()"):
                    del newMethods[num][nxtNum]

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if "" == nxtMethod:
                    del newMethods[num][nxtNum]

        finalMethods = []
        for method in newMethods:
            if len(method) > 1:
                finalMethods.append(" ".join(method) + "{}")
            else:
                finalMethods.append(method[0] + "{}")

        return list(dict.fromkeys(finalMethods))


    def constructFile( self, packageName ):

        folder = "C:/Users/Lalu/Downloads/2020_OOP_UE_Angabe1/project2"
        pages = [ [self.classNameSpecifier()], self.classFields(), self.classConstructors(), self.classMethods()]


        dir = os.path.join(folder, packageName)

        try:
            os.mkdir(dir)
        except FileExistsError :
            os.chdir(dir)

        filePath = os.path.join(os.getcwd(), self.getTitle()) + ".txt"
        #print("filePath: ", filePath)

        with open(filePath, "w") as file:
            for obj in pages:
                for element in obj:
                    file.write("\n")
                    file.writelines(element)
                    file.write("\n")

            file.write("\n")
            file.write("}")






class JavaException( HTMLFile ):

    def __init__( self, fileName ):
        super().__init__( fileName )
        self.className = self.getTitle()

    def deleteLinks( self, list ):

        newList = []
        for num, tag in enumerate( list ):
            if "<a href=" in tag:
                index = tag.find("<a")
                for itr, str in enumerate( tag[index:] ):
                    if ">" == str:
                        newTag = tag[itr+index:]
                        #print("new Tag : ", newTag)
                        newList.append( newTag )
                        break
                continue

            newList.append( tag )
        return newList


    def classNameSpecifier( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<span class="typeNameLabel">' in tag:
                classNameSpecifier = tag.split(">")[1].split( "<" )[0] + self.className

            if "extends <a" in tag:
                extends = tag.split( "<" )[1].split( ">" )[-1]
                if "Object" not in extends:
                    classNameSpecifier += " extends " + extends

            if "implements <a" in tag:
                implements = tag.split( "<" )[1].split( ">" )[-1]
                classNameSpecifier += " implements " + implements
                break;

        return (classNameSpecifier + "{")

    def classFields( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Field Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ========= CONSTRUCTOR DETAIL ======== -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        #fields = self.deleteLinks( fields )
        classFields = []

        for num, field in enumerate( fields ):
            if "<h4>" in field:
                fieldName = self.tagDestroyer( field )
                fieldSpecifier = fields[num+1]
                specificField = self.deleteLinks( [fieldSpecifier] )[0]
                if specificField.startswith( "<pre>" ):
                    newField = specificField.split( ";" )[-1].split( "</pre>" )[0]
                    newField = "private " + newField + ";"
                    classFields.append( newField )

                elif specificField.startswith( ">" ):

                    if "<a href=" in specificField:
                        delLink = self.deleteLinks([specificField])[0]
                        inSharpParenthesis = delLink.split( "</a>" )[0][1:] + ">"
                        fieldName = delLink.split( ";" )[-1].split( "<" )[0]
                        newField = "private " + specificField.split( "</a>" )[0][1:] + "<" + inSharpParenthesis + fieldName + ";"
                        classFields.append( newField )

                    else:
                        fieldType = specificField.split( "</a>" )[0][1:]
                        fieldName = specificField.split( "</a>" )[1].split( "</pre>" )[0]
                        newField = "private " + fieldType + fieldName + ";"
                        classFields.append( newField )

        return list(dict.fromkeys(classFields))

    def makePrettier( self, element ):

        return element.replace("&nbsp;", " ").replace("</a>", "").replace("<pre>", "").replace("</pre>", "")

    def classConstructors( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Constructor Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ============ METHOD DETAIL ========== -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        newConstructor = []
        for num, tag in enumerate( fields ):
            if "<h4>" in tag:
                constructorName = self.tagDestroyer( tag )
                oneConstructor = []
            if "<pre>" in tag:
                for newTag in fields[num:]:
                    if "</pre>" in newTag:
                        oneConstructor.append( self.makePrettier(newTag.strip()))
                        newConstructor.append(oneConstructor)
                        break
                    else:
                        oneConstructor.append(self.makePrettier(newTag.strip()))

        #print("new Constr before ", newConstructor)

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr ):
                if "<a href=" in nxtConstr:
                    processedConstr = nxtConstr
                    while (processedConstr.find("<a href=") != -1):
                        processedConstr = nxtConstr[:nxtConstr.find("<a href")] + nxtConstr[nxtConstr.find(">")+1:]
                        newConstructor[num][nxtNum] = processedConstr
                        nxtConstr = processedConstr

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr ):
                newConstructor[num][nxtNum] = nxtConstr.replace("&lt;", "<").replace("&gt;", ">")

        finalConsructors = []

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr[:-1] ):
                if "," in nxtConstr:
                    finalConsructors.append(" ".join(constr)+"{}")
                else:
                    finalConsructors.append(nxtConstr+"{}")

        return list(dict.fromkeys(finalConsructors))

    def classMethods( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Method Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ========= END OF CLASS DATA ========= -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        newMethods = []
        for num, tag in enumerate( fields ):
            if "<h4>" in tag:
                #methodName = self.tagDestroyer( tag )
                oneMethod = []
            if "<pre>" in tag:
                for newTag in fields[num:]:
                    if "</pre>" in newTag:
                        oneMethod.append( self.makePrettier(newTag.strip()))
                        newMethods.append(oneMethod)
                        break
                    else:
                        oneMethod.append(self.makePrettier(newTag.strip()))

        #print("newMethod: ", newMethods)

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if "<a href=" in nxtMethod:
                    processedMethod = nxtMethod
                    while (processedMethod.find("<a href=") != -1):
                        processedMethod = nxtMethod[:nxtMethod.find("<a href")] + nxtMethod[nxtMethod.find(">")+1:]
                        newMethods[num][nxtNum] = processedMethod
                        nxtMethod = processedMethod

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                newMethods[num][nxtNum] = nxtMethod.replace("&lt;", "<").replace("&gt;", ">")

        for num, method in enumerate( newMethods ):
            newMethods[num] = list(dict.fromkeys(method))

        #print("newMethod : ", newMethods)

        newMethodsList = []
        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if nxtMethod.startswith("x.deepCopy()"):
                    del newMethods[num][nxtNum]

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if nxtMethod.startswith("x.deepCopy()"):
                    del newMethods[num][nxtNum]

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if "" == nxtMethod:
                    del newMethods[num][nxtNum]

        finalMethods = []
        for method in newMethods:
            if len(method) > 1:
                finalMethods.append(" ".join(method) + "{}")
            else:
                finalMethods.append(method[0] + "{}")

        return list(dict.fromkeys(finalMethods))


    def constructFile( self, packageName ):

        folder = "C:/Users/Lalu/Downloads/2020_OOP_UE_Angabe1/project2"
        pages = [ [self.classNameSpecifier()], self.classFields(), self.classConstructors(), self.classMethods()]


        dir = os.path.join(folder, packageName)

        try:
            os.mkdir(dir)
        except FileExistsError :
            os.chdir(dir)

        filePath = os.path.join(os.getcwd(), self.getTitle()) + ".txt"
        #print("filePath: ", filePath)

        with open(filePath, "w") as file:
            for obj in pages:
                for element in obj:
                    file.write("\n")
                    file.writelines(element)
                    file.write("\n")

            file.write("\n")
            file.write("}")


class JavaInterface( HTMLFile ):

    def __init__( self, fileName ):
        super().__init__( fileName )
        self.className = self.getTitle()

    def deleteLinks( self, list ):

        newList = []
        for num, tag in enumerate( list ):
            if "<a href=" in tag:
                index = tag.find("<a")
                for itr, str in enumerate( tag[index:] ):
                    if ">" == str:
                        newTag = tag[itr+index:]
                        #print("new Tag : ", newTag)
                        newList.append( newTag )
                        break
                continue

            newList.append( tag )
        return newList


    def classNameSpecifier( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<span class="typeNameLabel">' in tag:
                classNameSpecifier = tag.split(">")[1].split( "<" )[0] + self.className

            if "extends <a" in tag:
                extends = tag.split( "<" )[1].split( ">" )[-1]
                if "Object" not in extends:
                    classNameSpecifier += " extends " + extends

            if "implements <a" in tag:
                implements = tag.split( "<" )[1].split( ">" )[-1]
                classNameSpecifier += " implements " + implements
                break;

        return (classNameSpecifier + "{")

    def classFields( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Field Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ========= CONSTRUCTOR DETAIL ======== -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        #fields = self.deleteLinks( fields )
        classFields = []

        for num, field in enumerate( fields ):
            if "<h4>" in field:
                fieldName = self.tagDestroyer( field )
                fieldSpecifier = fields[num+1]
                specificField = self.deleteLinks( [fieldSpecifier] )[0]
                if specificField.startswith( "<pre>" ):
                    newField = specificField.split( ";" )[-1].split( "</pre>" )[0]
                    newField = "private " + newField + ";"
                    classFields.append( newField )

                elif specificField.startswith( ">" ):

                    if "<a href=" in specificField:
                        delLink = self.deleteLinks([specificField])[0]
                        inSharpParenthesis = delLink.split( "</a>" )[0][1:] + ">"
                        fieldName = delLink.split( ";" )[-1].split( "<" )[0]
                        newField = "private " + specificField.split( "</a>" )[0][1:] + "<" + inSharpParenthesis + fieldName + ";"
                        classFields.append( newField )

                    else:
                        fieldType = specificField.split( "</a>" )[0][1:]
                        fieldName = specificField.split( "</a>" )[1].split( "</pre>" )[0]
                        newField = "private " + fieldType + fieldName + ";"
                        classFields.append( newField )

        return list(dict.fromkeys(classFields))

    def makePrettier( self, element ):

        return element.replace("&nbsp;", " ").replace("</a>", "").replace("<pre>", "").replace("</pre>", "")

    def classConstructors( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Constructor Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ============ METHOD DETAIL ========== -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        newConstructor = []
        for num, tag in enumerate( fields ):
            if "<h4>" in tag:
                constructorName = self.tagDestroyer( tag )
                oneConstructor = []
            if "<pre>" in tag:
                for newTag in fields[num:]:
                    if "</pre>" in newTag:
                        oneConstructor.append( self.makePrettier(newTag.strip()))
                        newConstructor.append(oneConstructor)
                        break
                    else:
                        oneConstructor.append(self.makePrettier(newTag.strip()))

        #print("new Constr before ", newConstructor)

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr ):
                if "<a href=" in nxtConstr:
                    processedConstr = nxtConstr
                    while (processedConstr.find("<a href=") != -1):
                        processedConstr = nxtConstr[:nxtConstr.find("<a href")] + nxtConstr[nxtConstr.find(">")+1:]
                        newConstructor[num][nxtNum] = processedConstr
                        nxtConstr = processedConstr

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr ):
                newConstructor[num][nxtNum] = nxtConstr.replace("&lt;", "<").replace("&gt;", ">")

        finalConsructors = []

        for num, constr in enumerate( newConstructor ):
            for nxtNum, nxtConstr in enumerate( constr[:-1] ):
                if "," in nxtConstr:
                    finalConsructors.append(" ".join(constr)+"{}")
                else:
                    finalConsructors.append(nxtConstr+"{}")

        return list(dict.fromkeys(finalConsructors))

    def classMethods( self ):

        for num, tag in enumerate( self.getFile() ):
            if '<h3>Method Detail</h3>' in tag:
                for nextNum, nextTag in enumerate( self.getFile() ):
                    if '<!-- ========= END OF CLASS DATA ========= -->' in nextTag:
                        fields = self.getFile()[num:nextNum]
                        break
                break
            else:
                fields = []

        newMethods = []
        for num, tag in enumerate( fields ):
            if "<h4>" in tag:
                #methodName = self.tagDestroyer( tag )
                oneMethod = []
            if "<pre>" in tag:
                for newTag in fields[num:]:
                    if "</pre>" in newTag:
                        oneMethod.append( self.makePrettier(newTag.strip()))
                        newMethods.append(oneMethod)
                        break
                    else:
                        oneMethod.append(self.makePrettier(newTag.strip()))

        #print("newMethod: ", newMethods)

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if "<a href=" in nxtMethod:
                    processedMethod = nxtMethod
                    while (processedMethod.find("<a href=") != -1):
                        processedMethod = nxtMethod[:nxtMethod.find("<a href")] + nxtMethod[nxtMethod.find(">")+1:]
                        newMethods[num][nxtNum] = processedMethod
                        nxtMethod = processedMethod

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                newMethods[num][nxtNum] = nxtMethod.replace("&lt;", "<").replace("&gt;", ">")

        for num, method in enumerate( newMethods ):
            newMethods[num] = list(dict.fromkeys(method))

        #print("newMethod : ", newMethods)

        newMethodsList = []
        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if nxtMethod.startswith("x.deepCopy()"):
                    del newMethods[num][nxtNum]

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if nxtMethod.startswith("x.deepCopy()"):
                    del newMethods[num][nxtNum]

        for num, method in enumerate( newMethods ):
            for nxtNum, nxtMethod in enumerate( method ):
                if "" == nxtMethod:
                    del newMethods[num][nxtNum]

        finalMethods = []
        for method in newMethods:
            if len(method) > 1:
                finalMethods.append(" ".join(method) + "{}")
            else:
                finalMethods.append(method[0] + "{}")

        return list(dict.fromkeys(finalMethods))


    def constructFile( self, packageName ):

        folder = "C:/Users/Lalu/Downloads/2020_OOP_UE_Angabe1/project2"
        pages = [ [self.classNameSpecifier()], self.classFields(), self.classConstructors(), self.classMethods()]


        dir = os.path.join(folder, packageName)

        try:
            os.mkdir(dir)
        except FileExistsError :
            os.chdir(dir)

        filePath = os.path.join(os.getcwd(), self.getTitle()) + ".txt"
        #print("filePath: ", filePath)

        with open(filePath, "w") as file:
            for obj in pages:
                file.write("\n")
                for element in obj:
                    file.write("\n")
                    file.writelines(element)
                    file.write("\n")

            file.write("\n")
            file.write("}")








file = "C:/Users/Lalu/Downloads/2020_OOP_UE_Beispiel2_Angabe/2020_OOP_UE_Beispiel2_Angabe/doc/overview-frame.html"
htmlFile = HTMLFile( file )

packages = htmlFile.createPackages()

try:
    folder = "C:/Users/Lalu/Downloads/2020_OOP_UE_Angabe1/project2"
    os.mkdir(folder)
    os.chdir(folder)
    print(os.getcwd())
except FileExistsError :
    os.chdir(folder)
    print(os.getcwd())




allPackages = []


for page in packages:
    #print(page.getFileName(), page.hierarchy, page.getFileLinks())
    #print("link", page.getFileLinks())
    #print("link title : ", page.getFileLinks())
    package = Package( page.getFileName()[:-18], page.hierarchy, page.getFileLinks() )
    package.generatePackage()
    allPackages.append( package )

print("allPackages: ", allPackages)

for package in allPackages:
    package.getAllName()




'''Created The Individual Packages and each files included in them
    now extract file information
    then make files'''
