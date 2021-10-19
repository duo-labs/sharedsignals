from typing import Optional, Type, TypeVar
from swagger_server.models import (Subject, SimpleSubject, ComplexSubject, Aliases,
                                   Account, DID, Email, IssSub, JwtID, Opaque,
                                   PhoneNumber, SamlAssertionID)


SimpleSubjectType = TypeVar(
    'SimpleSubjectType',
    # TODO codegen this list somewhere with a custom template
    # (the list must be static, thus we can't refer to SimpleSubject class at runtime)
    Account, DID, Email, IssSub, JwtID, Opaque, PhoneNumber, SamlAssertionID,
)


def get_simple_subject(subject: Subject, simple_subj_type: Type[SimpleSubjectType]) -> Optional[SimpleSubjectType]:
    subj_root = subject.__root__
    if isinstance(subj_root, SimpleSubject):
        # return the simplesubject as long as it matches simple_subj_type
        simple_subj = subj_root.__root__
        return simple_subj if isinstance(simple_subj, simple_subj_type) else None
    elif isinstance(subj_root, Aliases):
        # iterate through all identifiers, return the first that matches simple_subj_type
        return next(
            (i.__root__ for
            i in subj_root.identifiers
            if isinstance(i.__root__, simple_subj_type)),
            None
        )
    elif isinstance(subj_root, ComplexSubject):
        # iterate through all fields, return the first that matches simple_subj_type
        return next(
            (subj.__root__
            for subj in vars(subj_root).values()
            if subj and isinstance(subj.__root__, simple_subj_type)),
            None
        )
    else:
        return None
