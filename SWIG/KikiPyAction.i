
// --------------------------------------------------------------------------------------------------------

class KikiPyAction : public KikiAction
{
    public: // ........................................................................ PUBLIC

            KikiPyAction 	( PyObject * pyself, PyObject * object, const std::string & name, 
                                    int duration = 0, int mode = KikiAction::CONTINUOUS );
            ~KikiPyAction	();

};
