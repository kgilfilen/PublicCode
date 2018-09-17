#ifndef __RefCount_h__
#define __RefCount_h__

// Taken from Dr Dobbs, 1997: 
// http://www.drdobbs.com/cpp/a-template-for-reference-counting/184403382
//
// adapted by Kenny Gilfilen, September 2018
//
// This is similar to a reference counter template I wrote in 2001 for  a 
// Presence Server project at Evolving Systems, Inc. We used it with the 
// really complex objects, in order to reduce the over head of copying when
// objects are not changed. The Copy constructor was overwritten, to hand out 
// references, and only when a mutator on the object was invoked did we do a
// new deep copy, delete the reference, and decrement the ref count. We made it
// a template class so that we could use it on multiple types of classes. A 
// reference counter is part of a "smart pointer", in some cases.
//
// I have added comments to explain what each part does. I would not add these
// comments to regular code, because they are too detailed. In regular code, I 
// mostly comment on authorial intent only, because most developers can figure 
// out what the code is doing, just not what you meant for it to do.

template<class DATA>
class CHReferenceCount
{
public:
    CHReferenceCount();
    CHReferenceCount(const CHReferenceCount<DATA>& objRefCount);
    ~CHReferenceCount();
    CHReferenceCount<DATA>&
      operator=(const CHReferenceCount<DATA> &robjRefCount);
    void Reset();

protected:
    inline const DATA* const GetData() const;
    inline DATA* const GetData();

private:
    // Reference counting implementation
    void CopyOnWrite();
    void CopyReference(const CHReferenceCount<DATA>& robjRefCount);
    void NewReference();
    void ReleaseReference();
    
    inline int ReferenceCount();

    DATA*  m_pRefData;  // pointer to shared data structure
    int*  m_pnRefCount; // pointer to reference counter
};

///////////////////////////////////////////////////////////////////
// inline functions

template<class DATA>
inline const DATA* const CHReferenceCount<DATA>::GetData() const
{
    return m_pRefData;
}

// if an object is to be changed, this provides a new object for 
// modification using the CopyOnWrite() method, which also decrements
// the ref counter, or if this was the only reference, deletes 
// the object 
template<class DATA>
inline DATA* const CHReferenceCount<DATA>::GetData()
{
    if (ReferenceCount() > 1)
        CopyOnWrite();
    return m_pRefData;
}

// accessor for the current ref count
template<class DATA>
inline int CHReferenceCount<DATA>::ReferenceCount()
{
    return *m_pnRefCount;
}

///////////////////////////////////////////////////////////////////
// out-of-line functions
//
// constructor--in this case the user is creating a new object. Future
// instances of this, that is, copies of this, will get a reference to 
// this, until a mutator is invoked.
template<class DATA>
CHReferenceCount<DATA>::CHReferenceCount()
{
    NewReference();
}

// copy constructor--in this case you are handing out a new reference
// to the original object, not a whole new object.
template<class DATA>
CHReferenceCount<DATA>::CHReferenceCount
    (const CHReferenceCount<DATA>& robjRefCount)
{ 
    CopyReference(robjRefCount);
}

//destructor
template<class DATA>
CHReferenceCount<DATA>::~CHReferenceCount()
{
    ReleaseReference();
}

// assignment operator--in this case, you are handing out a new
// reference, not a new object. 
template<class DATA>
CHReferenceCount<DATA>&

CHReferenceCount<DATA>::operator=
    (const CHReferenceCount<DATA>& robjRefCount)
{
    if (robjRefCount.m_pRefData != m_pRefData)
    {
        ReleaseReference();
        CopyReference(robjRefCount);
    }

    return(*this);
}

// used by the copy constructor or assignment operator;
// this copies the reference of the original object to this new 
// object and increments the ref count.
template<class DATA>
void CHReferenceCount<DATA>::CopyReference
    (const CHReferenceCount<DATA>& robjRefCount)
{
    ASSERT(robjRefCount.m_pRefData && robjRefCount.m_pnRefCount);
    
    m_pRefData = robjRefCount.m_pRefData;
    m_pnRefCount = robjRefCount.m_pnRefCount;
    ++*m_pnRefCount;
}

template<class DATA>
void CHReferenceCount<DATA>::NewReference()
{
    m_pRefData = new DATA;
    m_pnRefCount = new int(1);
}

// when the user is doing a write, or deleting an object, this
// method decrements the ref count, and if it is the last one, 
// deletes the ref entirely. It then also deletes the object,
// and removes the pointer.
template<class DATA>
void CHReferenceCount<DATA>::ReleaseReference()
{
    --*m_pnRefCount;
    
    if (*m_pnRefCount == 0)
    {
        delete m_pnRefCount;
        m_pnRefCount=NULL;

        delete m_pRefData;
        m_pRefData=NULL;
    }
}

// when the user is modifying the object, then we no longer want
// to just have a reference to it, we need a new one, and it will 
// be "written" with the changes. 
template<class DATA>
void CHReferenceCount<DATA>::CopyOnWrite()
{
    DATA* pRefData = new DATA(*m_pRefData);

    ReleaseReference();
    
    m_pRefData = pRefData;
    m_pnRefCount = new int(1);
}

// On the occasion that the user wants to start over with this 
// object, just removing references and starting with a new and 
// empty ref count and referenced DATA thang.
template<class DATA>
void CHReferenceCount<DATA>::Reset()
{
    ReleaseReference();
    m_pRefData =  new DATA;
    m_pnRefCount = new int(1);
}

#endif
//End of File